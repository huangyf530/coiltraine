import torch
import torch.nn as nn
import torch.utils.model_zoo as model_zoo
import torch.nn.functional as F


__all__ = ['erfnet']

model_urls = {
    'ERFnet': 'https://github.com/adrshm91/erfnet_pytorch/tree/master/trained_models/erfnet_pretrained.pth',
}


class DownsamplerBlock (nn.Module):
    def __init__(self, ninput, noutput):
        super().__init__()

        self.conv = nn.Conv2d(ninput, noutput-ninput, (3, 3), stride=2, padding=1, bias=True)
        self.pool = nn.MaxPool2d(2, stride=2)
        self.bn = nn.BatchNorm2d(noutput, eps=1e-3)

    def forward(self, input):
        print([self.conv(input).size(), self.pool(input).size()])
        output = torch.cat([self.conv(input), self.pool(input)], 1)
        output = self.bn(output)
        return F.relu(output)


class non_bottleneck_1d(nn.Module):
    def __init__(self, chann, dropprob, dilated):
        super().__init__()

        self.conv3x1_1 = nn.Conv2d(chann, chann, (3, 1), stride=1, padding=(1, 0), bias=True)

        self.conv1x3_1 = nn.Conv2d(chann, chann, (1, 3), stride=1, padding=(0, 1), bias=True)

        self.bn1 = nn.BatchNorm2d(chann, eps=1e-03)

        self.conv3x1_2 = nn.Conv2d(chann, chann, (3, 1), stride=1, padding=(1 * dilated, 0), bias=True,
                                   dilation=(dilated, 1))

        self.conv1x3_2 = nn.Conv2d(chann, chann, (1, 3), stride=1, padding=(0, 1 * dilated), bias=True,
                                   dilation=(1, dilated))

        self.bn2 = nn.BatchNorm2d(chann, eps=1e-03)

        self.dropout = nn.Dropout2d(dropprob)

    def forward(self, input):
        output = self.conv3x1_1(input)
        output = F.relu(output)
        output = self.conv1x3_1(output)
        output = self.bn1(output)
        output = F.relu(output)

        output = self.conv3x1_2(output)
        output = F.relu(output)
        output = self.conv1x3_2(output)
        output = self.bn2(output)

        if (self.dropout.p != 0):
            output = self.dropout(output)

        return F.relu(output + input)  # +input = identity (residual connection)


class Encoder(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        self.initial_block = DownsamplerBlock(3, 16)  # 100 * 44

        self.layers = nn.ModuleList()

        # self.layers.append(DownsamplerBlock(16, 64))

        for x in range(0, 5):  # 5 times
            self.layers.append(non_bottleneck_1d(16, 0.03, 1))

        self.layers.append(DownsamplerBlock(16, 64))  # 50 * 22

        for x in range(0, 1):  # 1 times
            self.layers.append(non_bottleneck_1d(64, 0.3, 2))
            self.layers.append(non_bottleneck_1d(64, 0.3, 4))
            self.layers.append(non_bottleneck_1d(64, 0.3, 8))
            self.layers.append(non_bottleneck_1d(64, 0.3, 16))

        # Only in encoder mode:
        self.output_conv = nn.Conv2d(64, num_classes, 1, stride=1, padding=0, bias=True)

    def forward(self, input, predict=False):
        output = self.initial_block(input)

        for layer in self.layers:
            output = layer(output)

        if predict:
            output = self.output_conv(output)

        return output


class UpsamplerBlock(nn.Module):
    def __init__(self, ninput, noutput):
        super().__init__()
        self.conv = nn.ConvTranspose2d(ninput, noutput, 3, stride=2, padding=1, output_padding=1, bias=True)
        self.bn = nn.BatchNorm2d(noutput, eps=1e-3)

    def forward(self, input):
        output = self.conv(input)
        output = self.bn(output)
        return F.relu(output)


class Decoder(nn.Module):
    def __init__(self, num_classes):
        super().__init__()

        self.layers = nn.ModuleList()

        self.layers.append(UpsamplerBlock(64, 16))
        self.layers.append(non_bottleneck_1d(16, 0, 1))
        self.layers.append(non_bottleneck_1d(16, 0, 1))

        # self.layers.append(UpsamplerBlock(64, 16))
        # self.layers.append(non_bottleneck_1d(16, 0, 1))
        # self.layers.append(non_bottleneck_1d(16, 0, 1))

        self.output_conv = nn.ConvTranspose2d(16, num_classes, 2, stride=2, padding=0, output_padding=0, bias=True)

    def forward(self, input):
        output = input

        for layer in self.layers:
            output = layer(output)

        output = self.output_conv(output)

        return output


# ERFNet
class Net(nn.Module):
    def __init__(self, num_classes, encoder=None):  # use encoder to pass pretrained encoder
        super().__init__()

        if encoder == None:
            self.encoder = Encoder(2)
            self.fc = nn.Linear(35200, num_classes)
        else:
            self.encoder = encoder
            self.fc = nn.Linear(70400, num_classes)
        self.decoder = Decoder(2)

    def forward(self, input, only_encode=False):
        if only_encode:
            output = self.encoder.forward(input, predict=True)
            return self.fc(output), None
        else:
            output = self.encoder(input)  # predict=False by default
            output = self.decoder.forward(output)
            print("output", output.size())
            return self.fc(output), None


def erfnet(num_classes, pretrained=False):
    """Constructs a erfnet model.

    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
    """
    model = Net(num_classes=num_classes)
    # if pretrained:
    #     model_dict = model_zoo.load_url(model_urls['ERFnet'])
    #     state = model.state_dict()
    #     state.update(model_dict)
    #     model.load_state_dict(state)

    return model