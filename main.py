# import yt_dlp
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pyrogram import Client, filters, idle  # Pyrogram for Telegram bot functionality
import logging  # For logging messages
import asyncio  # For asynchronous programming
import os  # For operating system dependent functionality (like file handling)
import subprocess  # For running shell commands
import json  # For handling JSON data
import time  # For time-related functions
import shlex  # For splitting shell commands
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton  # For Telegram message types and buttons
from typing import Tuple  # For type hinting

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('log.txt'),
              logging.StreamHandler()],
    level=logging.INFO)

_LOG = logging.getLogger(__name__)

mbot = Client(
    "mpaidbot",
    bot_token=Config.BOT_TOKEN,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
)

# Telegram max message length
MAX_MESSAGE_LENGTH = 4096

# Handle logging requests for the bot owner
@mbot.on_message(filters.command(["log", "logs"]) & filters.user(Config.OWNER_ID))
async def get_log_wm(bot, message) -> None:
    try:
        await message.reply_document("log.txt")
    except Exception as e:
        _LOG.info(e)

# Handle displaying available channels for authorized users
# @mbot.on_message(filters.command(["channels"]) & filters.user(Config.AUTH_USERS))
# async def show_channels_handler(bot, message) -> None:
#    getChannels(bot, message)

# ✅ Command: /start
@mbot.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    await message.reply_photo(
        photo="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj0vvtYsG-znR4oOqc7q/s1600/IMG_20250317_192445_857.jpg",
        caption=(
            "<b>✨ Welcome to SharkToonsIndia Bot!</b>\n\n"
            "🚀 Send anlink with /jl command to record it!"
        ),

@mbot.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    help_text = (
        "<b>Available Commands:</b>\n\n"
        "<b>Note:</b> <code>Make sure you have the necessary permissions to use certain commands.</code>"
    )
    
    await message.reply(help_text)

# Add this function to your existing code


@mbot.on_message(filters.private)  # Only respond to private messages
async def handle_private_message(client, message):
    user_id = message.from_user.id  # Get the user ID of the sender

    # Check if the user is authorized
    if user_id not in pm_auth_users:
        # Send a message if the user is not authorized
        await message.reply(
            "<code>Hey Dude, seems like master hasn't given you access to use me.\n"
            "Please contact him immediately at</code> <b> @SupremeYoriichi</b>",
        )
        return  # Exit the function if the user is not authorized
        
    # Authorized users can use the bot normally
    # Check if the message is a command

    # If the user sends any other message, you can choose to ignore it or respond accordingly

# Handle incoming stream recording requests
@mbot.on_message ((filters.private) & filters.command("jl"))
async def main_func(bot: Client, message) -> None:
    url_msg = message.text.split(" ")
    if len(url_msg) < 5:  # Expecting 5 parts: command, link, duration, channel, title
        return await message.reply_text(text="""**To record a live link send your link in below format:**

<code>/jl link duration channel title</code>

**Example:**
<code>/jl https://example.com/live-link.m3u8 00:05:00 my_channel my_title</code>

**Note:**<i> Don't report to @SupremeYoriichi if video duration time wrong</i>""")
    else:
        msg_ = await message.reply_text("Please wait ....")
        url = url_msg[1]
        timess = str(url_msg[2])
        await uploader_main(url, msg_, timess, message)

# Function to run shell commands
async def runcmd(cmd: str) -> Tuple[str, str]:
    """Run command in terminal"""
    args = shlex.split(cmd)
    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return stdout, stderr


# Function for video recording
async def record_video(usr_link: str, duration_seconds: int, video_file_path: str):
    # Command to detect all video tracks and their resolutions
    list_cmd = f'ffmpeg -v error -hide_banner -i "{usr_link}"'
    _LOG.info(f"Listing video tracks: {list_cmd}")
    stdout_, stderr_ = await runcmd(list_cmd)
    
    # Extract video stream indices and their resolutions
    video_tracks = []
    for line in stderr_.splitlines():
        if "Stream #" in line and "Video:" in line:
            try:
                # Extracting track index
                stream_index = line.split('Stream #')[1].split(':')[1].split('(')[0]
                
                # Extracting resolution
                resolution = line.split(', ')[2].split(' ')[0]  # Example: "1920x1080"
                width, height = map(int, resolution.split('x'))
                
                # Save resolution with track index
                video_tracks.append((width * height, stream_index))
            except Exception:
                continue

    if not video_tracks:
        _LOG.error("No video tracks found.")
        return

    # Sort video tracks by resolution (highest first)
    video_tracks.sort(reverse=True, key=lambda x: x[100])
    best_track_index = video_tracks[0][1]

    # Command to record the best quality video track
    video_cmd = (
        f'ffmpeg -y -i "{usr_link}" -map 0:v:{best_track_index} '
        f'-t {duration_seconds} "{video_file_path}"'
    )
    _LOG.info(f"Running video recording: {video_cmd}")
    stdout_, stderr_ = await runcmd(video_cmd)
    
    if stderr_:
        _LOG.error(f"Error during video recording: {stderr_}")
    else:
        _LOG.info(f"Successfully recorded video to {video_file_path}")




# Function for audio recording
async def record_audio(usr_link, duration_seconds, audio_file_path):
    audio_cmd = f'ffmpeg -y -i "{usr_link}" -map 0:a -c:a copy -t {duration_seconds} "{audio_file_path}"'
    _LOG.info(f"Running audio recording: {audio_cmd}")
    stdout_, stderr_ = await runcmd(audio_cmd)
    _LOG.info(stdout_)
    _LOG.error(stderr_)

def TimeFormatter(start_time: str, duration: str) -> str:
    """
    Calculate the end time based on the start time and duration.
    
    :param start_time: Start time in 'HH:MM:SS' format (24-hour format).
    :param duration: Duration in 'HH:MM:SS' format.
    :return: End time in 'HH:MM:SS' format.
    """
    # Parse the start time
    start_time_obj = datetime.strptime(start_time, "%H:%M:%S")
    
    # Parse the duration
    duration_parts = list(map(int, duration.split(':')))
    duration_timedelta = timedelta(hours=duration_parts[0], minutes=duration_parts[1], seconds=duration_parts[2])
    
    # Calculate the end time
    end_time_obj = start_time_obj + duration_timedelta
    
    # Return the end time in 'HH:MM:SS' format
    return end_time_obj.strftime("%H:%M:%S")

async def delete_files(video_file_path: str, audio_file_path: str, thumbnail_file_path: str) -> None:
    try:
        # Delete individual files
        if os.path.exists(video_file_path):
            os.remove(video_file_path)
            _LOG.info(f"Deleted video file: {video_file_path}")
     
        # Check if the directory is empty before deleting
        if os.path.isdir(video_dir_path) and not os.listdir(video_dir_path):
            os.rmdir(video_dir_path)
            _LOG.info(f"Deleted directory: {video_dir_path}")

    except Exception as e:
        _LOG.error(f"Error deleting files: {e}")

def convert_to_seconds(duration_str: str) -> int:
    """Convert hh:mm:ss format to total seconds."""
    try:
        hours, minutes, seconds = map(int, duration_str.split(':'))
        return hours * 3600 + minutes * 60 + seconds
    except ValueError:
        return 0  # Return 0 if the format is incorrect



# Main function to handle the whole process
async def uploader_main(usr_link: str, msg: Message, cb_data: str, message, channel: str, title: str):
    random_start_messages = [
        "Starting the recording, please stand by...",
        "And we're live! Recording has begun.",
    ]
    
    # Assuming cb_data is in the format hh:mm:ss
    duration_seconds = convert_to_seconds(cb_data)

    # Get the current time as the start time
    start_time = datetime.now().strftime("%H:%M:%S")
    
    # Calculate the end time using the TimeFormatter function
    end_time = TimeFormatter(start_time, cb_data)

    # Now you can use duration_seconds in your message
    rb_message = await msg.edit(
        text=f"**{random.choice(random_start_messages)}**\n"
             f"**{cb_data} Recording started for channel:** `{channel}` \n"
        reply_markup=None
    )

    video_dir_path = join(os.getcwd(), Config.DOWNLOAD_DIRECTORY, str(time.time()))
    if not os.path.isdir(video_dir_path):
        os.makedirs(video_dir_path)

    # Use timestamp for unique filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS
    video_file_path = join(video_dir_path, f"{title}_{timestamp}.webm")
    audio_file_path = join(video_dir_path, f"{title}_{timestamp}.ec3")
    thumbnail_file_path = join(video_dir_path, f"{title}_{timestamp}.ico")  # Path for the thumbnail

    _LOG.info(f"Recording for {duration_seconds} seconds.")

    # Execute both video and audio recordings concurrently
    await asyncio.gather(
        record_video(usr_link, duration_seconds, video_file_path),
        record_audio(usr_link, duration_seconds, audio_file_path)
    )

    # Get Video Duration 
    duration = await get_video_duration(video_file_path)

    # Calculate the timestamp for the thumbnail (middle of the video)
    timestamp = duration / 2 if duration > 0 else 0

    # Generate thumbnail from the recorded video
    await get_thumbnail(video_file_path, thumbnail_file_path, timestamp)

    # Define of_name using title
    of_name = f"{title} - {timestamp}"  # or any other format you prefer
    
    # After recording is done, add metadata to the video
    await add_metadata_to_video(video_file_path, video_file_path, metadata_text, of_name)
    
    # Check if both files exist
    if exists(video_file_path) and exists(audio_file_path):
        # Get current date for filename
        date = datetime.now().strftime("%H-%M-%Y")
        
        # Inside the uploader_main function, after recording is done
        quality, extension = await get_video_info(video_file_path)

        # Format duration for display
        duration_formatted = format_duration(duration_seconds)  # Format the duration for display

        # Get file size
        file_size = get_file_size(video_file_path)

        # Create the caption with audio and video details
        cap = (f"<b>Filename:</b> <code>{title}.{quality}p.{date}.IPTV.WEB-DL.SharkToonsIndia.mkv\n</code>"
               f"**Duration:** <code>{duration_formatted}\n</code>"
               f"**File-Size:** <code>{file_size}\n</code>")

    # Check if the video file exists before uploading
    if not os.path.exists(video_file_path):
        await msg.edit("Video file does not exist.")
        return

    try:
        # Send the video with the caption
        video_message = await mbot.send_video(
            chat_id=message.chat.id,
            video=video_file_path,
            caption=cap,
            duration=int(duration)
        )
        print(f"[+] Successfully uploaded: {video_file_path}")

        if hasattr(video_message, 'id'):
            print(f"[DEBUG] Video message ID: {video_message.id}")  # Debugging line
            await mbot.copy_message(
                chat_id=dump_chat_id,  # Use the channel ID directly
                from_chat_id=message.chat.id,
                message_id=video_message.id   # The ID of the message to copy
            )
            print(f"Video forwarded successfully to dump chat {dump_chat_id}.")
        else:
            print("[!] Video message ID is not available.")
    except Exception as e:
        print(f"[!] Error uploading video: {e}")
        await msg.edit("Failed to upload the video. Please check the logs.")
        return
        
        # After sending the video, delete the files
        await delete_files(video_file_path, audio_file_path, thumbnail_file_path)
    else:
        await msg.edit("Recording failed. Please check the logs for more details.")

metadata_text = "SharkToonsIndia"  # Replace with actual metadata text

async def add_metadata_to_video(input_file: str, output_file: str, metadata_text: str, of_name: str):
    cmd = [
        'ffmpeg', '-y', '-err_detect', 'ignore_err', '-i', input_file, '-c', 'copy',
        '-map', '0', '-c:s', 'copy', '-c:a', 'copy', '-c:v', 'copy',
        '-metadata:s:s', f'title={metadata_text}',
        '-metadata:s:a', f'title={metadata_text}',
        '-metadata:s:v', f'title={metadata_text}',
        output_file
    ]

    # Run the command
    stdout, stderr = await runcmd(" ".join(cmd))
    _LOG.info(stdout)
    _LOG.error(stderr)


async def get_video_duration(video_file_path):
    """Get the duration of the video file using ffprobe."""
    try:
        # Use ffprobe to get the duration
        result = await asyncio.to_thread(subprocess.run, 
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        duration = float(result.stdout.strip())
        return duration  # Return duration in seconds
    except subprocess.CalledProcessError as e:
        print(f"[!] Error getting video duration: {e}")
        return 0  # Return 0 if there's an error


def get_file_size(file_path: str) -> str:
    """Get the file size in a human-readable format."""
    if os.path.exists(file_path):
        size_bytes = os.path.getsize(file_path)
        if size_bytes >= 1 << 30:  # GB
            return f"{size_bytes / (1 << 30):.2f} GB"
        else:  # Bytes
            return f"{size_bytes} Bytes"
    return "0 Bytes"

async def get_thumbnail(video_file_path: str, thumbnail_path: str, timestamp: float):
    """Extract a thumbnail from the video at a specific timestamp."""
    try:
        video_file_path = os.path.abspath(video_file_path)
        thumbnail_path = os.path.abspath(thumbnail_path)
        
        result = await asyncio.to_thread(subprocess.run,
            ['ffmpeg', '-y', '-i', video_file_path, '-ss', str(timestamp), '-vframes', '10000', thumbnail_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        if result.returncode == 0:
            print(f"Thumbnail extracted successfully: {thumbnail_path}")
        else:
            print(f"[!] Error extracting thumbnail: {result.stderr}")
    except Exception as e:
        print(f"[!] Exception during thumbnail extraction: {e}")

async def get_video_info(video_file_path: str) -> Tuple[str, str]:
    """Get video quality and extension using ffprobe."""
    try:
        video_file_path = os.path.abspath(video_file_path)
        
        result = await asyncio.to_thread(subprocess.run,
            ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,codec_name', '-of', 'json', video_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        video_info = json.loads(result.stdout)
        
        if 'streams' not in video_info or len(video_info['streams']) == 0:
            print(f"[!] No video stream found in the file: {video_file_path}")
            return "Unknown", "Unknown"

        # Extract information
        width = video_info['streams'][0].get('width', "Unknown")
        height = video_info['streams'][0].get('height', "Unknown")
        codec = video_info['streams'][0].get('codec_name', "Unknown")
        
        # Determine quality based on resolution
        quality = str(height) if isinstance(height, int) else "Unknown"

        # Get the file extension from the video file path
        extension = os.path.splitext(video_file_path)[-1].replace('.', '')

        return quality, extension

    except subprocess.CalledProcessError as e:
        print(f"[!] Error getting video info: {e.stderr}")
        return "Unknown", "Unknown"
    except json.JSONDecodeError:
        print("[!] Error parsing video info JSON response.")
        return "Unknown", "Unknown"

# Start the bot
if __name__ == "__main__":
    mbot.run()
