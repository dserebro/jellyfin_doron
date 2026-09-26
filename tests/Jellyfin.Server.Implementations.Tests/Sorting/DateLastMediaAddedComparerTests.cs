using System;
using Jellyfin.Server.Implementations.Sorting;
using MediaBrowser.Controller.Entities;
using MediaBrowser.Controller.Entities.Movies;
using Xunit;

namespace Jellyfin.Server.Implementations.Tests.Sorting;

public class DateLastMediaAddedComparerTests
{
    private readonly DateLastMediaAddedComparer _cmp = new DateLastMediaAddedComparer();

    [Fact]
    public void Compare_NullItem_HandlesGracefully()
    {
        var folder = new Folder { DateLastMediaAdded = new DateTime(2024, 1, 1) };

        Assert.True(_cmp.Compare(null, folder) < 0);
        Assert.True(_cmp.Compare(folder, null) > 0);
    }

    [Fact]
    public void Compare_FolderWithDateVsFolderWithoutDate_SortsCorrectly()
    {
        var withDate = new Folder { DateLastMediaAdded = new DateTime(2024, 1, 1) };
        var withoutDate = new Folder();

        Assert.True(_cmp.Compare(withDate, withoutDate) > 0);
        Assert.True(_cmp.Compare(withoutDate, withDate) < 0);
    }

    [Fact]
    public void Compare_EqualDates_ReturnsZero()
    {
        var a = new Folder { DateLastMediaAdded = new DateTime(2024, 6, 15) };
        var b = new Folder { DateLastMediaAdded = new DateTime(2024, 6, 15) };

        Assert.Equal(0, _cmp.Compare(a, b));
    }

    [Fact]
    public void Compare_NonFolderItems_ReturnsZero()
    {
        Assert.Equal(0, _cmp.Compare(new Movie(), new Movie()));
    }
}
