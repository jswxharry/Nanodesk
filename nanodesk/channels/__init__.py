"""Nanodesk Channels - 自定义频道

添加你的个人频道适配。
"""


def get_custom_channels():
    """返回所有自定义频道实例
    
    在 bootstrap.py 中调用注册。
    """
    channels = []
    
    # TODO: 添加你的频道
    # from nanodesk.channels.my_channel import MyChannel
    # channels.append(MyChannel())
    
    return channels


def register_channels():
    """注册所有自定义频道"""
    from nanobot.channels.manager import ChannelManager
    
    for channel in get_custom_channels():
        ChannelManager.register(channel)
