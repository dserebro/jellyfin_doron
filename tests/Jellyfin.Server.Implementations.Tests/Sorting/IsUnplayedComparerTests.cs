using System;
using Jellyfin.Database.Implementations.Entities;
using Jellyfin.Server.Implementations.Sorting;
using MediaBrowser.Controller.Entities;
using MediaBrowser.Controller.Entities.Movies;
using MediaBrowser.Controller.Library;
using Moq;
using Xunit;

namespace Jellyfin.Server.Implementations.Tests.Sorting;

public sealed class IsUnplayedComparerTests : IDisposable
{
    private readonly IUserDataManager _savedUserDataManager = BaseItem.UserDataManager;

    public void Dispose() => BaseItem.UserDataManager = _savedUserDataManager;

    private static User CreateUser() => new User("test-user", "auth-provider", "reset-provider");

    [Fact]
    public void Compare_NullItem_HandlesGracefully()
    {
        var user = CreateUser();
        var item = new Movie();

        var mockDataManager = new Mock<IUserDataManager>();
        mockDataManager
            .Setup(m => m.GetUserData(user, item))
            .Returns(new UserItemData { Key = "unplayed", Played = false });

        BaseItem.UserDataManager = mockDataManager.Object;

        var cmp = new IsUnplayedComparer { User = user };

        Assert.True(cmp.Compare(null, item) > 0);
        Assert.True(cmp.Compare(item, null) < 0);
    }

    [Fact]
    public void Compare_NullUser_ThrowsArgumentNullException()
    {
        var cmp = new IsUnplayedComparer();

        Assert.Throws<ArgumentNullException>(() => cmp.Compare(new Movie(), new Movie()));
    }

    [Fact]
    public void Compare_UnplayedVsPlayed_UnplayedSortsFirst()
    {
        var user = CreateUser();
        var playedItem = new Movie();
        var unplayedItem = new Movie();

        var mockDataManager = new Mock<IUserDataManager>();
        mockDataManager
            .Setup(m => m.GetUserData(user, playedItem))
            .Returns(new UserItemData { Key = "played", Played = true });
        mockDataManager
            .Setup(m => m.GetUserData(user, unplayedItem))
            .Returns(new UserItemData { Key = "unplayed", Played = false });

        BaseItem.UserDataManager = mockDataManager.Object;

        var cmp = new IsUnplayedComparer { User = user };

        Assert.True(cmp.Compare(unplayedItem, playedItem) < 0);
        Assert.True(cmp.Compare(playedItem, unplayedItem) > 0);
    }
}
