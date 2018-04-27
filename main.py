import time
import random

from InstagramAPI import InstagramAPI

from config import *
from logger import logger
from db import *


def main():
    logger.info("\n")
    logger.info("-----------------------")

    api = InstagramAPI(insta_account, insta_password)

    api.login()

    api.getUsernameInfo(api.username_id)
    selfUserInfo = api.LastJson['user']
    logger.info("Follower Count: %d" %selfUserInfo.get('follower_count', 0))
    logger.info("Following Count: %d" %selfUserInfo.get('following_count', 0))
    time.sleep(random.randint(minDelay_betweenAction, maxDelay_betweenAction))

    api.getHashtagFeed(hashtag)
    tag_items = api.LastJson.get('items', [])
    time.sleep(random.randint(minDelay_betweenAction, maxDelay_betweenAction))

    users = [x.get('user') for x in tag_items]
    usernames = []
    for user in users:
        following = user.get('friendship_status').get('following')
        username = user.get('username')
        user_id = user.get('pk')

        if not (username in usernames) and not following and not noResponse_checking(username):

            logger.info("Following %s " % username)
            api.follow(user_id)
            add_row(Following, [username, user_id, date.today()])
            usernames.append(username)
            time.sleep(random.randint(minDelay_betweenAction, maxDelay_betweenAction))

        if len(usernames) > limitation_per_session-1:
            break

    expiration_followings = expired_followings(waiting_days)
    for expiration_following in expiration_followings:

        api.userFriendship(str(expiration_following.userId))
        friendship_status = api.LastJson
        time.sleep(random.randint(minDelay_betweenAction, maxDelay_betweenAction))

        if friendship_status.get('followed_by'):
            logger.Info("%s followed me reversely" % expiration_following.username)
            add_row(Response, [expiration_following.username, expiration_following.userId, datetime.now() +
                               timedelta(hours=delay_autoMessage)])
        else:
            logger.Info("%s have not followed me for past %ddays"%(expiration_following.username, waiting_days))
            add_row(NoResponse, expiration_following.username)
            api.unfollow(expiration_following.userId)
            time.sleep(random.randint(minDelay_betweenAction, maxDelay_betweenAction))

    for row in friends_for_am():
        userId = row.userId
        api.direct_message(str(userId), message_content)
        logger.info("Sending private message to %s" % row.username)
        delete_row(row)
        time.sleep(random.randint(minDelay_betweenAction, maxDelay_betweenAction))


if __name__ == "__main__":
    sleeping_time = random.randint(0, 3600)
    logger.info("Sleeping: %s s" % str(sleeping_time))
    time.sleep(sleeping_time)

    for i in range(session_limitations):
        time.sleep(random.randint(minDelay_betweenSession, maxDelay_betweenSession))
        main()


    # api = InstagramAPI(insta_account, insta_password)
    #
    # api.login()
    #
    # api.getHashtagFeed(hashtag)
    # tag_items = api.LastJson.get('items', [])
    # print (tag_items)

    # api.userFriendship('5348044429')
    # print (api.LastJson)



