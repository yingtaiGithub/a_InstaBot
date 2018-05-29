import time
import random

import imageio
try:
    from InstagramAPI import InstagramAPI
except imageio.core.fetching.NeedDownloadError:
    imageio.plugins.ffmpeg.download()
    from InstagramAPI import InstagramAPI

from config import *
from logger import logger
from db import *


def action_delay(action):
    logger.info(action)
    random_sleep = random.randint(minDelay_betweenAction, maxDelay_betweenAction)
    logger.info("Sleeping: %s s" % str(random_sleep))
    time.sleep(random_sleep)


def get_users_by_hashtag(api, hashtags):
    users = []
    for hashtag in hashtags:
        api.getHashtagFeed(hashtag)
        tag_items = api.LastJson.get('items', [])

        action_delay("Got Users by hashtag '%s' - %s" % hashtag)

        users.extend([x.get('user') for x in tag_items])

    return users


def get_users_by_profile(api, profiles):
    users = []
    for profile in profiles:
        username = profile.replace("@", '')
        api.searchUsername(username)
        usernameId = api.LastJson.get('user').get('pk')

        action_delay('Id of %s - %s' % (profile, usernameId))

        next_max_id = ''
        api.getUserFollowers(usernameId, next_max_id)
        temp = api.LastJson
        users.extend(temp['users'])

        action_delay("Got Followers of the profile '%s'" % profile)

    return users


def following_users(api, users):
    usernames = []
    for user in users:
        username = user.get('username')
        user_id = user.get('pk')
        # following = user.get('friendship_status').get('following')

        api.userFriendship(user_id)
        following = api.LastJson.get('following')
        followed_by = api.LastJson.get('followed_by')
        action_delay("Friendship with %s: Following %s , Followed_by %s" % (username, following, followed_by))

        if not (username in usernames) and not following and not followed_by and not noResponse_checking(username):
            api.follow(user_id)
            add_row(Following, [username, user_id, date.today(), 0])
            usernames.append(username)

            action_delay("Following %s " % username)
        if len(usernames) > limitation_per_session - 1:
            break


def check_expiredFollowings(api):
    expiration_followings = expired_followings(waiting_days)
    for expiration_following in expiration_followings:

        api.userFriendship(str(expiration_following.userId))
        friendship_status = api.LastJson

        # time.sleep(random.randint(minDelay_betweenAction, maxDelay_betweenAction))

        if friendship_status.get('followed_by'):
            logger.info("%s followed me reversely" % expiration_following.username)
            add_row(Response, [expiration_following.username, expiration_following.userId, datetime.now() +
                               timedelta(hours=delay_autoMessage)])

            add_row(Following,
                    [expiration_following.username, expiration_following.userId, expiration_following.taken_at, 1])

        else:
            logger.info("%s have not followed me for past %ddays" % (expiration_following.username, waiting_days))
            add_row(NoResponse, [expiration_following.username])

            api.unfollow(expiration_following.userId)
            action_delay("Unfollowed %s " % expiration_following.username)

            delete_row(expiration_following)


def auto_messaging(api):
    for row in friends_for_am():
        userId = row.userId
        api.direct_message(str(userId), message_content)

        delete_row(row)

        action_delay("Sending private message to %s" % row.username)


def getTotalFollowings(api):
    followers = []
    next_max_id = ''
    while True:
        api.getUserFollowings(api.username_id, next_max_id)
        temp = api.LastJson
        action_delay("Getting total Following")

        for item in temp["users"]:
            # follower = [item.get('username'), item.get('pk')]
            followers.append(item)

        if temp["big_list"] is False:
            return followers
        next_max_id = temp["next_max_id"]


def save_manually_followings(api):
    logger.info('Getting and saving the followings you follow manually.')
    total_followers = getTotalFollowings(api)
    for follower in total_followers:
        if not check_existing(Following, follower.get('username')):
            add_row(Following, [follower.get('username'), follower.get('pk'), date.today(), 0])


def get_existingFollowing(api):
    logger.info('Getting and saving the existing followings')
    total_followers = getTotalFollowings(api)
    for follower in total_followers:
        add_row(
            Following, [follower.get('username'), follower.get('pk'), date.today()-timedelta(days=waiting_days+1), 1])


def main(get_manually_followings):
    api = InstagramAPI(insta_account, insta_password)

    api.login()

    api.getUsernameInfo(api.username_id)
    selfUserInfo = api.LastJson['user']
    logger.info("Follower Count: %d" %selfUserInfo.get('follower_count', 0))
    logger.info("Following Count: %d" %selfUserInfo.get('following_count', 0))
    action_delay('')

    if not get_first_row(Following):
        get_existingFollowing(api)
    else:
        weekday = datetime.today().weekday()
        if weekday == 0 and get_manually_followings:
            save_manually_followings(api)

    users = get_users_by_profile(api, profiles)

    users.extend(get_users_by_hashtag(api, hashtags))

    following_users(api, users)

    check_expiredFollowings(api)

    auto_messaging(api)

    api.logout()


if __name__ == "__main__":
#   Create db
    Base.metadata.create_all(engine)

    sleeping_time = random.randint(0, 2400)
    logger.info("Initial Sleeping: %s s" % str(sleeping_time))
    time.sleep(sleeping_time)

    for i in range(session_limitations):
        logger.info("\n")
        logger.info("-----------------------")
        sleeping_time = random.randint(minDelay_betweenSession, maxDelay_betweenSession)
        logger.info("Sleeping between session %s s")
        time.sleep(sleeping_time)

        if i == 0:
            get_manually_followings = True
        else:
            get_manually_followings = False

        main(get_manually_followings)

        logger.info("End Session")
