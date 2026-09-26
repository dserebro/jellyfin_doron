using System;
using Jellyfin.Database.Implementations.Entities;
using Jellyfin.Server.Implementations.Sorting;
using MediaBrowser.Controller.Entities;
using MediaBrowser.Controller.Entities.Movies;
using MediaBrowser.Controller.Library;
using Moq;
using Xunit;

namespace Jellyfin.Server.Implementations.Tests.Sorting;

public sealed class IsFavoriteOrLikeComparerTests : IDisposable
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
            .Returns(new UserItemData { Key = "fav", IsFavorite = true });

        BaseItem.UserDataManager = mockDataManager.Object;

        var cmp = new IsFavoriteOrLikeComparer { User = user };

        Assert.True(cmp.Compare(null, item) > 0);
        Assert.True(cmp.Compare(item, null) < 0);
    }

    [Fact]
    public void Compare_NullUser_ThrowsArgumentNullException()
    {
        var cmp = new IsFavoriteOrLikeComparer();

        Assert.Throws<ArgumentNullException>(() => cmp.Compare(new Movie(), new Movie()));
    }

    [Fact]
    public void Compare_FavoriteVsNonFavorite_FavoriteSortsFirst()
    {
        var user = CreateUser();
        var favoriteItem = new Movie { Id = Guid.NewGuid() };
        var normalItem = new Movie { Id = Guid.NewGuid() };

        var mockDataManager = new Mock<IUserDataManager>();
        mockDataManager
            .Setup(m => m.GetUserData(It.IsAny<User>(), favoriteItem))
            .Returns(new UserItemData { Key = "fav", IsFavorite = true });
        mockDataManager
            .Setup(m => m.GetUserData(It.IsAny<User>(), normalItem))
            .Returns(new UserItemData { Key = "normal", IsFavorite = false });

        BaseItem.UserDataManager = mockDataManager.Object;

        var cmp = new IsFavoriteOrLikeComparer { User = user };

        Assert.True(cmp.Compare(favoriteItem, normalItem) < 0);
        Assert.True(cmp.Compare(normalItem, favoriteItem) > 0);
    }
}
