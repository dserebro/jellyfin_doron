using System;
using Jellyfin.Server.Implementations.HttpServer;
using MediaBrowser.Controller.Net;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Logging.Abstractions;
using Moq;
using Xunit;

namespace Jellyfin.Server.Implementations.Tests.HttpServer;

public class WebSocketManagerTests
{
    [Fact]
    public void Constructor_NullAuthService_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => new WebSocketManager(
            null!,
            Array.Empty<IWebSocketListener>(),
            NullLogger<WebSocketManager>.Instance,
            Mock.Of<ILoggerFactory>()));
    }

    [Fact]
    public void Constructor_NullWebSocketListeners_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => new WebSocketManager(
            Mock.Of<IAuthService>(),
            null!,
            NullLogger<WebSocketManager>.Instance,
            Mock.Of<ILoggerFactory>()));
    }

    [Fact]
    public void Constructor_NullLogger_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => new WebSocketManager(
            Mock.Of<IAuthService>(),
            Array.Empty<IWebSocketListener>(),
            null!,
            Mock.Of<ILoggerFactory>()));
    }

    [Fact]
    public void Constructor_NullLoggerFactory_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => new WebSocketManager(
            Mock.Of<IAuthService>(),
            Array.Empty<IWebSocketListener>(),
            NullLogger<WebSocketManager>.Instance,
            null!));
    }
}
