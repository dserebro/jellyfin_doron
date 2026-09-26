#pragma warning disable CS1591

using System;
using Jellyfin.Data.Enums;
using Jellyfin.Database.Implementations.Entities;
using MediaBrowser.Controller.Entities;
using MediaBrowser.Controller.Library;
using MediaBrowser.Controller.Sorting;

namespace Jellyfin.Server.Implementations.Sorting
{
    public class IsPlayedComparer : IUserBaseItemComparer
    {
        /// <summary>
        /// Gets or sets the user.
        /// </summary>
        /// <value>The user.</value>
        public User User { get; set; } = null!;

        /// <summary>
        /// Gets the name.
        /// </summary>
        /// <value>The name.</value>
        public ItemSortBy Type => ItemSortBy.IsUnplayed;

        /// <summary>
        /// Gets or sets the user data manager.
        /// </summary>
        /// <value>The user data manager.</value>
        public IUserDataManager UserDataManager { get; set; } = null!;

        /// <summary>
        /// Gets or sets the user manager.
        /// </summary>
        /// <value>The user manager.</value>
        public IUserManager UserManager { get; set; } = null!;

        /// <summary>
        /// Compares the specified x.
        /// </summary>
        /// <param name="x">The x.</param>
        /// <param name="y">The y.</param>
        /// <returns>System.Int32.</returns>
        public int Compare(BaseItem? x, BaseItem? y)
        {
            return GetValue(x).CompareTo(GetValue(y));
        }

        /// <summary>
        /// Gets the date.
        /// </summary>
        /// <param name="x">The x.</param>
        /// <returns>DateTime.</returns>
        private int GetValue(BaseItem? x)
        {
            ArgumentNullException.ThrowIfNull(User);

            if (x is null)
            {
                return 1;
            }

            return x.IsPlayed(User, userItemData: null) ? 0 : 1;
        }
    }
}
