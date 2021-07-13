import logging
from django.conf import settings
from constance import config
import asyncio
import os
import sys
import json
from string import ascii_letters, digits
from random import choice
from typing import Optional
from choice.template import choice_text
from django.template import Context
from matrix.models import Account
from nio.responses import RoomCreateError, RoomInfo

from nio import (
    AsyncClient,
    ClientConfig,
    DevicesError,
    Event,
    InviteEvent,
    LoginResponse,
    LocalProtocolError,
    MatrixRoom,
    MatrixUser,
    RoomMessageText,
    crypto,
    exceptions,
    RoomSendResponse,
    RoomVisibility,
)
from nio.responses import RoomCreateError, RoomInfo

logger = logging.getLogger(__name__)

PASSWORD = settings.MATRIX_BOT_PASSWORD
SESSION_DETAILS_FILE = "credentials.json"

def random_string():
    return ''.join([choice(ascii_letters + digits) for i in range(32)])

# This is a fully-documented example of how to do manual verification with nio,
# for when you already know the device IDs of the users you want to trust. If
# you want live verification using emojis, the process is more complicated and
# will be covered in another example.

# We're building on the restore_login example here to preserve device IDs and
# therefore preserve trust; if @bob trusts @alice's device ID ABC and @alice
# restarts this program, loading the same keys, @bob will preserve trust. If
# @alice logged in again @alice would have new keys and a device ID XYZ, and
# @bob wouldn't trust it.

# The store is where we want to place encryption details like our keys, trusted
# devices and blacklisted devices. Here we place it in the working directory,
# but if you deploy your program you might consider /var or /opt for storage

# This file is for restoring login details after closing the program, so you
# can preserve your device ID. If @alice logged in every time instead, @bob
# would have to re-verify. See the restoring login example for more into.

# Only needed for this example, this is who @alice will securely
# communicate with. We need all the device IDs of this user so we can consider
# them "trusted". If an unknown device shows up (like @bob signs into their
# account on another device), this program will refuse to send a message in the
# room. Try it!

class CustomEncryptedClient(AsyncClient):
    def __init__(self, homeserver, user='', device_id='', store_path='', config=None, ssl=None, proxy=None):
        # Calling super.__init__ means we're running the __init__ method
        # defined in AsyncClient, which this class derives from. That does a
        # bunch of setup for us automatically
        super().__init__(homeserver, user=user, device_id=device_id, store_path=store_path, config=config, ssl=ssl, proxy=proxy)

        # if the store location doesn't exist, we'll make it
        if store_path and not os.path.isdir(store_path):
            os.mkdir(store_path)

        # auto-join room invites
        #self.add_event_callback(self.cb_autojoin_room, InviteEvent)

        # print all the messages we receive
        self.add_event_callback(self.cb_print_messages, RoomMessageText)

    async def login(self, user_id) -> None:
        """Log in either using the global variables or (if possible) using the
        session details file.

        NOTE: This method kinda sucks. Don't use these kinds of global
        variables in your program; it would be much better to pass them
        around instead. They are only used here to minimise the size of the
        example.
        """
        # Restore the previous session if we can
        # See the "restore_login.py" example if you're not sure how this works
        logger.debug(f"{self.user_id=}")
        logger.debug(f"{self.user=}")
        try:
            account = Account.objects.get(user_id=user_id)
        except Account.DoesNotExist:
            logger.error(f"No Account exists for {user_id}")
            sys.exit(1)
        self.user_id = user_id
        self.access_token = account.access_token
        self.device_id = account.device_id
        # We didn't restore a previous session, so we'll log in with a password
        if not self.access_token or not self.device_id:
            # this calls the login method defined in AsyncClient from nio
            password = account.password
            if not password:
                logger.warn(f"Password for Account {account} is empty")
                sys.exit(1)
            resp = await super().login(password)

            if isinstance(resp, LoginResponse):
                print("Logged in using a password; saving details to disk")
                self.__write_details_to_disk(resp)
            else:
                print(f"Failed to log in: {resp}")
                sys.exit(1)

    async def create_room(self, room_alias=None, room_name='', room_topic='') -> None:
        """Log in either using the global variables or (if possible) using the
        session details file.
        """
        if not room_alias:
            room_alias = random_string()
        # Restore the previous session if we can
        # See the "restore_login.py" example if you're not sure how this works
        self.load_store()
        logger.debug(f"Logged in using stored credentials: {self.user_id} on {self.device_id}")
        resp = await self.room_create(
            visibility=RoomVisibility.public,
            alias=room_alias,
            name=room_name,
            topic=room_topic,
        )
        return resp

    def trust_devices(self, user_id: str, device_list: Optional[str] = None) -> None:
        """Trusts the devices of a user.
        If no device_list is provided, all of the users devices are trusted. If
        one is provided, only the devices with IDs in that list are trusted.
        Arguments:
            user_id {str} -- the user ID whose devices should be trusted.

        Keyword Arguments:
            device_list {Optional[str]} -- The full list of device IDs to trust
                from that user (default: {None})
        """

        print(f"{user_id}'s device store: {self.device_store[user_id]}")

        # The device store contains a dictionary of device IDs and known
        # OlmDevices for all users that share a room with us, including us.

        # We can only run this after a first sync. We have to populate our
        # device store and that requires syncing with the server.
        for device_id, olm_device in self.device_store[user_id].items():
            if device_list and device_id not in device_list:
                # a list of trusted devices was provided, but this ID is not in
                # that list. That's an issue.
                print(f"Not trusting {device_id} as it's not in {user_id}'s pre-approved list.")
                continue

            if user_id == self.user_id and device_id == self.device_id:
                # We cannot explictly trust the device @alice is using
                continue

            self.verify_device(olm_device)
            print(f"Trusting {device_id} from user {user_id}")

    def cb_autojoin_room(self, room: MatrixRoom, event: InviteEvent):
        """Callback to automatically joins a Matrix room on invite.
        Arguments:
            room {MatrixRoom} -- Provided by nio
            event {InviteEvent} -- Provided by nio
        """
        self.join(room.room_id)
        #room = self.rooms[ROOM_ID]
        #print(f"Room {room.name} is encrypted: {room.encrypted}" )

    async def cb_print_messages(self, room: MatrixRoom, event: RoomMessageText):
        """Callback to print all received messages to stdout.

        Arguments:
            room {MatrixRoom} -- Provided by nio
            event {RoomMessageText} -- Provided by nio
        """
        if event.decrypted:
            encrypted_symbol = "🛡 "
        else:
            encrypted_symbol = "⚠️ "
        print(f"{room.display_name} |{encrypted_symbol}| {room.user_name(event.sender)}: {event.body}")

    async def join_room(self, room_id):
        # Now we send an encrypted message that @bob can read, although it will
        # appear to be "unverified" when they see it, because @bob has not verified
        # the device @alice is sending from.
        # We'll leave that as an excercise for the reader.
        await self.join(room_id)

    async def send_greeting(self, room_alias, greeting=''):
        # Now we send an encrypted message that @bob can read, although it will
        # appear to be "unverified" when they see it, because @bob has not verified
        # the device @alice is sending from.
        # We'll leave that as an excercise for the reader.
        try:
            resp = await self.room_send(
                room_alias,
                message_type="m.room.message",
                content = {
                    "msgtype": "m.text",
                    "body": greeting
                }
            )
            logger.debug(resp)
        except exceptions.OlmUnverifiedDeviceError as err:
            print("These are all known devices:")
            device_store: crypto.DeviceStore = device_store
            [print(f"\t{device.user_id}\t {device.device_id}\t {device.trust_state}\t  {device.display_name}") for device in device_store]
            sys.exit(1)


    @staticmethod
    def __write_details_to_disk(resp: LoginResponse) -> None:
        """Writes login details to disk so that we can restore our session later
        without logging in again and creating a new device ID.

        Arguments:
            resp {LoginResponse} -- the successful client login response.
        """
        """
        with open(SESSION_DETAILS_FILE, "w") as f:
            json.dump({
                "access_token": resp.access_token,
                "device_id": resp.device_id,
                "user_id": resp.user_id
            }, f)
        """
        try:
            account = Account.objects.get(user_id=resp.user_id)
        except Account.DoesNotExist:
            logger.error(f"No Account exists for {resp.user_id}")
            return
        logger.debug(f"{len(resp.access_token)=}")
        account.access_token = resp.access_token
        account.device_id = resp.device_id
        account.password = None
        account.save()

async def run_client(client: CustomEncryptedClient, user_id="", room_alias="") -> None:
    """A basic encrypted chat application using nio.
    """

    # This is our own custom login function that looks for a pre-existing config
    # file and, if it exists, logs in using those details. Otherwise it will log
    # in using a password.
    await client.login(user_id)
    # Here we create a coroutine that we can call in asyncio.gather later,
    # along with sync_forever and any other API-related coroutines you'd like
    # to do.
    async def after_first_sync():
        # We'll wait for the first firing of 'synced' before trusting devices.
        # client.synced is an asyncio event that fires any time nio syncs. This
        # code doesn't run in a loop, so it only fires once
        print("Awaiting sync")
        await client.synced.wait()

        # In practice, you want to have a list of previously-known device IDs
        # for each user you want ot trust. Here, we require that list as a
        # global variable
        #client.trust_devices(BOB_ID, BOB_DEVICE_IDS)

        # In this case, we'll trust _all_ of @alice's devices. NOTE that this
        # is a SUPER BAD IDEA in practice, but for the purpose of this example
        # it'll be easier, since you may end up creating lots of sessions for
        # @alice as you play with the script
        #client.trust_devices(ALICE_USER_ID)
        resp = await client.create_room(room_alias=room_alias)
        logger.warn(resp)
        room_id = resp.room_id
        resp = await client.join_room(room_id)
        logger.warn(f"{resp=}")
        resp = await client.send_greeting(room_id)
        logger.warn(f"{resp=}")

    # We're creating Tasks here so that you could potentially write other
    # Python coroutines to do other work, like checking an API or using another
    # library. All of these Tasks will be run concurrently.
    # For more details, check out https://docs.python.org/3/library/asyncio-task.html

    # ensure_future() is for Python 3.5 and 3.6 compatability. For 3.7+, use
    # asyncio.create_task()
    after_first_sync_task = asyncio.ensure_future(after_first_sync())

    # We use full_state=True here to pull any room invites that occured or
    # messages sent in rooms _before_ this program connected to the
    # Matrix server
    sync_forever_task = asyncio.ensure_future(client.sync_forever(30000, full_state=True))

    await asyncio.gather(
        # The order here IS significant! You have to register the task to trust
        # devices FIRST since it awaits the first sync
        after_first_sync_task,
        sync_forever_task
    )

async def run_create_room(
        client: CustomEncryptedClient,
        user_id="",
        room_alias="",
        room_name="",
        room_topic="",
        greeting="") -> None:
    """A basic encrypted chat application using nio.
    """
    resp = await client.login(user_id)
    logger.debug(resp)

    async def after_first_sync():
        # We'll wait for the first firing of 'synced' before trusting devices.
        # client.synced is an asyncio event that fires any time nio syncs. This
        # code doesn't run in a loop, so it only fires once
        logger.debug("Awaiting sync")
        #await client.synced.wait()
        sync_response = await client.sync(20000)
        logger.debug(sync_response)
        # In practice, you want to have a list of previously-known device IDs
        # for each user you want to trust. Here, we require that list as a
        # global variable
        #client.trust_devices(BOB_ID, BOB_DEVICE_IDS)
        # In this case, we'll trust _all_ of @alice's devices. NOTE that this
        # is a SUPER BAD IDEA in practice, but for the purpose of this example
        # it'll be easier, since you may end up creating lots of sessions for
        # @alice as you play with the script
        #client.trust_devices(ALICE_USER_ID)
        resp = await client.create_room(
            room_alias=room_alias,
            room_name=room_name,
            room_topic=room_topic,
        )
        if isinstance(resp, RoomCreateError):
            logger.error(f"RoomCreateErro {resp}")
            await client.close()
            return
        room_id = resp.room_id
        logger.debug(room_id)
        resp = await client.join_room(room_id)
        logger.debug(resp)
        resp = await client.send_greeting(room_id, greeting)
        logger.debug(resp)
        await client.close()
        return room_id

    # We're creating Tasks here so that you could potentially write other
    # Python coroutines to do other work, like checking an API or using another
    # library. All of these Tasks will be run concurrently.
    # For more details, check out https://docs.python.org/3/library/asyncio-task.html

    # ensure_future() is for Python 3.5 and 3.6 compatability. For 3.7+, use
    # asyncio.create_task()
    after_first_sync_task = asyncio.ensure_future(after_first_sync())
    sync_forever_task = asyncio.ensure_future(client.sync_forever(25000, full_state=True))

    resp = await asyncio.gather(
        # The order here IS significant! You have to register the task to trust
        # devices FIRST since it awaits the first sync
        after_first_sync_task,
        #sync_forever_task
    )
    return resp

async def main(
    user_id,
    room_alias,
    room_name='',
    room_topic='',
    greeting=''):
    # By setting `store_sync_tokens` to true, we'll save sync tokens to our
    # store every time we sync, thereby preventing reading old, previously read
    # events on each new sync.
    # For more info, check out https://matrix-nio.readthedocs.io/en/latest/nio.html#asyncclient
    config = ClientConfig(store_sync_tokens=True)
    try:
        account = Account.objects.get(user_id=user_id)
        logger.debug(f"{account=}")
    except Account.DoesNotExist:
        return
    store_path = f"{settings.MEDIA_ROOT}/{account.nio_store}"
    if store_path and not os.path.isdir(store_path):
        os.mkdir(store_path)
    client = CustomEncryptedClient(
        account.homeserver,
        account.user_id,
        store_path=store_path,
        config=config,
        ssl=False,
    )
    logger.debug(f"{client=}")
    try:
        resp = await run_create_room(
            client,
            user_id=user_id,
            room_alias=room_alias,
            room_name=room_name,
            room_topic=room_topic,
            greeting=greeting,
            )
    except (asyncio.CancelledError, KeyboardInterrupt):
        resp = None
        await client.close()
    return resp


class CreateRoomSync:


    def __init__(self, diploma, school):
        self.school = school
        self.diploma = diploma
        self.context = self.get_context()
        self.user_id = self.get_user_id()
        self.room_alias = self.get_room_alias()
        self.room_name = self.get_room_name()
        self.room_topic = self.get_room_topic()
        self.greeting = self.get_greeting()

    def get_context(self):
        return Context(
            {
                "diploma_slug": self.diploma.slug,    
                "diploma_label": self.diploma.label,
                "school_slug": self.school.slug,
                "school_tag": self.school.tag
            }
        )

    def get_user_id(self):
        return config.choice_matrix_bot_user_id

    def get_room_alias(self):
        return choice_text(self.context, "alias")

    def get_room_name(self):
        return choice_text(self.context, "name")

    def get_room_topic(self):
        return choice_text(self.context, "topic")

    def get_greeting(self):
        return choice_text(self.context, "greeting")

    def create(self):
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(
            main(
                self.user_id,
                room_alias=self.room_alias,
                room_name=self.room_name,
                room_topic=self.room_topic,
                greeting=self.greeting,
            )
        )
        return resp