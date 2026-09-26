using System;
using Jellyfin.Database.Implementations.Entities;
using Jellyfin.Server.Implementations.Sorting;
using MediaBrowser.Controller.Entities;
using MediaBrowser.Controller.Entities.Movies;
using MediaBrowser.Controller.Library;
using Moq;
using Xunit;

namespace Jellyfin.Server.Implementations.Tests.Sorting;

public class DatePlayedComparerTests
{
    private static User CreateUser() => new User("test-user", "auth-provider", "reset-provider");

    [Fact]
    public void Compare_NullItem_HandlesGracefully()
    {
        var user = CreateUser();
        var item = new Movie();

        var mockDataManager = new Mock<IUserDataManager>();
        mockDataManager
            .Setup(m => m.GetUserData(user, item))
            .Returns(new UserItemData { Key = "a", LastPlayedDate = new DateTime(2024, 1, 1), Played = true });

        var cmp = new DatePlayedComparer
        {
            User = user,
            UserDataManager = mockDataManager.Object,
            UserManager = new Mock<IUserManager>().Object
        };

        Assert.True(cmp.Compare(null, item) < 0);
        Assert.True(cmp.Compare(item, null) > 0);
    }

    [Fact]
    public void Compare_NullUser_ThrowsArgumentNullException()
    {
        var cmp = new DatePlayedComparer
        {
            UserDataManager = new Mock<IUserDataManager>().Object,
            UserManager = new Mock<IUserManager>().Object
        };

        Assert.Throws<ArgumentNullException>(() => cmp.Compare(new Movie(), new Movie()));
    }

    [Fact]
    public void Compare_ItemWithLaterPlayDate_SortsAfter()
    {
        var user = CreateUser();
        var itemA = new Movie { Id = Guid.NewGuid() };
        var itemB = new Movie { Id = Guid.NewGuid() };

        var mockDataManager = new Mock<IUserDataManager>();
        mockDataManager
            .Setup(m => m.GetUserData(It.IsAny<User>(), itemA))
            .Returns(new UserItemData { Key = "a", LastPlayedDate = new DateTime(2024, 1, 1), Played = true });
        mockDataManager
            .Setup(m => m.GetUserData(It.IsAny<User>(), itemB))
            .Returns(new UserItemData { Key = "b", LastPlayedDate = new DateTime(2024, 6, 1), Played = true });

        var cmp = new DatePlayedComparer
        {
            User = user,
            UserDataManager = mockDataManager.Object,
            UserManager = new Mock<IUserManager>().Object
        };

        Assert.True(cmp.Compare(itemA, itemB) < 0);
        Assert.True(cmp.Compare(itemB, itemA) > 0);
    }
}
