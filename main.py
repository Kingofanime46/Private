import asyncio
import os
import random

import discord
from discord.ext import commands

from keep_alive import keep_alive

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
funny_work_messages_file = "funny_work_messages.txt"

def load_funny_work_messages():
    with open(funny_work_messages_file, "r") as file:
        return [line.strip() for line in file.readlines()]


items = {
    "sword": {"name": "Sword", "price": 50, "effect": "Increased attack power"},
    "shield": {"name": "Shield", "price": 30, "effect": "Increased defense"},
    "potion": {"name": "Health Potion", "price": 20, "effect": "Heals a portion of health"},
    # Add more items as needed
}


funny_work_messages = load_funny_work_messages()
work_counters = {message: 0 for message in funny_work_messages}

@bot.event
async def on_message(message):
    if not message.author.bot:  # Ignore messages from bots
        userid = message.author.id
        wallet_file = f"wallet/{userid}.txt"
        bank_file = f"bank/{userid}.txt"
        inventory_file = f"inventory/{userid}.txt"

        if not os.path.isfile(inventory_file):
             with open(inventory_file, "w") as new_inventory:
                new_inventory.write("{}")
             await message.channel.send(f"Welcome {message.author.mention}! Your inventory has been created.")

        if not os.path.isfile(wallet_file):
            with open(wallet_file, "w") as new_wallet:
                new_wallet.write("0")
            await message.channel.send(f"Welcome {message.author.mention}! Your wallet has been created with an initial balance of 0 electricity.")

        if not os.path.isfile(bank_file):
            with open(bank_file, "w") as new_bank:
                new_bank.write("1000")
            await message.channel.send(f"Welcome {message.author.mention}! Your bank account has been created with an initial balance of 1000 electricity.")

    await bot.process_commands(message)

@bot.command()
async def balance(ctx, target_user: discord.Member = None):
    userid = ctx.message.author.id
    user = ctx.message.author
    target_user = target_user or ctx.author

    userid = target_user.id
    user = target_user
    wallet_file = f"wallet/{userid}.txt"
    bank_file = f"bank/{userid}.txt"

    wallet_balance = int(open(wallet_file, "r").read())
    bank_balance = int(open(bank_file, "r").read())

    embed = discord.Embed(
        title=f"{user.name}'s Finances",
        description=f"Wallet Balance: **{wallet_balance}** electricity\nBank Balance: **{bank_balance}** electricity",
        color=0x3498db
    )
    embed.set_thumbnail(url=user.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def deposit(ctx, amount: int):
    userid = ctx.message.author.id
    user = ctx.message.author

    if amount <= 0:
        await ctx.send("Please enter a valid positive amount to deposit.")
        return

    wallet_file = f"wallet/{userid}.txt"
    bank_file = f"bank/{userid}.txt"

    wallet_balance = int(open(wallet_file, "r").read())
    wallet_balance -= amount
    with open(wallet_file, "w") as wallet:
        wallet.write(str(wallet_balance))

    bank_balance = int(open(bank_file, "r").read())
    bank_balance += amount
    with open(bank_file, "w") as bank:
        bank.write(str(bank_balance))

    embed = discord.Embed(
        title="Deposit Successful",
        description=f"{user.name} deposited {amount} electricity to the bank.",
        color=0x2ecc71
    )
    embed.set_thumbnail(url=user.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def withdraw(ctx, amount: int):
    userid = ctx.message.author.id
    user = ctx.message.author

    if amount <= 0:
        await ctx.send("Please enter a valid positive amount to withdraw.")
        return

    wallet_file = f"wallet/{userid}.txt"
    bank_file = f"bank/{userid}.txt"

    wallet_balance = int(open(wallet_file, "r").read())
    bank_balance = int(open(bank_file, "r").read())

    bank_balance -= amount
    with open(bank_file, "w") as bank:
        bank.write(str(bank_balance))

    wallet_balance += amount
    with open(wallet_file, "w") as wallet:
        wallet.write(str(wallet_balance))

    embed = discord.Embed(
        title="Withdrawal Successful",
        description=f"{user.name} withdrew {amount} electricity from the bank.",
        color=0x2ecc71
    )
    embed.set_thumbnail(url=user.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def pay(ctx, recipient: discord.User, amount: int):
    sender_userid = ctx.message.author.id
    sender_user = ctx.message.author
    recipient_userid = recipient.id

    if amount <= 0:
        await ctx.send("Please enter a valid positive amount to transfer.")
        return

    sender_wallet_file = f"wallet/{sender_userid}.txt"
    recipient_wallet_file = f"wallet/{recipient_userid}.txt"

    sender_balance = int(open(sender_wallet_file, "r").read())
    recipient_balance = int(open(recipient_wallet_file, "r").read())

    sender_balance -= amount
    with open(sender_wallet_file, "w") as sender_wallet:
        sender_wallet.write(str(sender_balance))

    recipient_balance += amount
    with open(recipient_wallet_file, "w") as recipient_wallet:
        recipient_wallet.write(str(recipient_balance))

    embed = discord.Embed(
        title="Payment Successful",
        description=f"{sender_user.name} paid {recipient.name} {amount} electricity.",
        color=0x2ecc71
    )
    embed.set_thumbnail(url=sender_user.display_avatar.url)
    await ctx.send(embed=embed)
@bot.command()
async def buy(ctx, item_id: str, quantity: int = 1):
      userid = ctx.message.author.id
      wallet_file = f"wallet/{userid}.txt"
      inventory_file = f"inventory/{userid}.txt"

      if item_id not in items:
          await ctx.send("Invalid item ID. Please check the item shop for valid items.")
          return

      item_info = items[item_id]
      total_price = item_info["price"] * quantity

      # Check if the user has enough money to buy the items
      wallet_balance = int(open(wallet_file, "r").read())
      if wallet_balance < total_price:
          await ctx.send("You don't have enough electricity to buy this item.")
          return

      # Deduct the price from the user's wallet
      wallet_balance -= total_price
      with open(wallet_file, "w") as wallet:
          wallet.write(str(wallet_balance))

      # Load and update the user's inventory
      try:
          with open(inventory_file, "r") as file:
              inventory = eval(file.read())
      except FileNotFoundError:
          inventory = {}

      # Update the inventory with the purchased items
      if item_id not in inventory:
          inventory[item_id] = 0

      inventory[item_id] += quantity

      # Save the updated inventory
      with open(inventory_file, "w") as file:
          file.write(str(inventory))

      # Send a purchase confirmation message
      embed = discord.Embed(
          title="Purchase Successful",
          description=f"You bought {quantity} {item_info['name']} for {total_price} electricity.",
          color=0x2ecc71
      )
      await ctx.send(embed=embed)

@bot.command()
async def shop(ctx):
    embed = discord.Embed(
        title="Item Shop",
        description="Welcome to the item shop! Buy items to enhance your adventure.",
        color=0x3498db
    )

    for item_id, item_info in items.items():
        embed.add_field(
            name=f"**{item_info['name']}** (ID: {item_id})",
            value=f"Price: {item_info['price']} electricity\nEffect: {item_info['effect']}",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.command()
async def iteminfo(ctx, item_id: str):
    if item_id not in items:
        await ctx.send("Invalid item ID. Please check the item shop for valid items.")
        return

    item_info = items[item_id]
    embed = discord.Embed(
        title=f"{item_info['name']} (ID: {item_id})",
        description=f"Price: {item_info['price']} electricity\nEffect: {item_info['effect']}",
        color=0x3498db
    )

    await ctx.send(embed=embed)

@bot.command()
async def inventory(ctx):
    userid = ctx.message.author.id
    inventory_file = f"inventory/{userid}.txt"
    try:
        with open(inventory_file, "r") as file:
            inventory = eval(file.read())
    except FileNotFoundError:
        inventory = {}

    if not inventory:
        await ctx.send("Your inventory is empty. Visit the item shop to buy items.")
        return

    embed = discord.Embed(
        title="Inventory",
        description="Here are the items in your inventory:",
        color=0x3498db
    )

    for item_id, quantity in inventory.items():
        item_info = items[item_id]
        embed.add_field(
            name=f"**{item_info['name']}** (ID: {item_id})",
            value=f"Quantity: {quantity}\nEffect: {item_info['effect']}",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.command()
@commands.cooldown(1, 60, commands.BucketType.user)
async def work(ctx):
    userid = ctx.message.author.id
    user = ctx.message.author

    # Your work logic here (modify as needed)
    earnings = random.randint(1, 1000)

    
  
    work_message = random.choice(funny_work_messages)
  # Update the counter for the chosen message
    work_counters[work_message] += 1

    # Update user's wallet
    wallet_file = f"wallet/{userid}.txt"
    current_balance = int(open(wallet_file, "r").read())
    new_balance = current_balance + earnings
    with open(wallet_file, "w") as wallet:
        wallet.write(str(new_balance))

    counter = work_counters[work_message]
    embed = discord.Embed(
        title="Work Successful",
        description=f"{user.name}, {work_message} {earnings} electricity\n\n* reply #{counter} .*",
        color=0x2ecc71
    )
    embed.set_thumbnail(url=user.display_avatar.url)
    print(f"DEBUG: work_message: {work_message}")
    await ctx.send(embed=embed)

@work.error
async def work_cooldown(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(description=f"You cannot work for {error.retry_after:.0f} seconds")
        await ctx.send(embed=embed)

@bot.command()
async def rob(ctx, target: discord.User):
    robber_userid = ctx.message.author.id
    robber_wallet_file = f"wallet/{robber_userid}.txt"

    target_userid = target.id
    target_wallet_file = f"wallet/{target_userid}.txt"

    # Check if the target has money to rob
    target_balance = int(open(target_wallet_file, "r").read())
    if target_balance <= 0:
        await ctx.send(f"{target.name} has no money to rob.")
        return

    # Attempt to rob
    success_chance = random.randint(1, 100)
    if success_chance <= 50:
        # Successful robbery
        rob_amount = random.randint(1, target_balance)
        target_balance -= rob_amount
        with open(target_wallet_file, "w") as target_wallet:
            target_wallet.write(str(target_balance))

        # Add the stolen amount to the robber's wallet
        robber_balance = int(open(robber_wallet_file, "r").read())
        robber_balance += rob_amount
        with open(robber_wallet_file, "w") as robber_wallet:
            robber_wallet.write(str(robber_balance))

        embed = discord.Embed(
            title="Robbery Successful",
            description=f"{ctx.message.author.name} successfully robbed {target.name} and stole {rob_amount} electricity!",
            color=0x2ecc71
        )
        await ctx.send(embed=embed)
    else:
        # Failed robbery
        rob_penalty = random.randint(1, 1000)
        robber_balance = int(open(robber_wallet_file, "r").read())
        robber_balance -= rob_penalty
        with open(robber_wallet_file, "w") as robber_wallet:
            robber_wallet.write(str(robber_balance))

        embed = discord.Embed(
            title="Robbery Failed",
            description=f"{ctx.message.author.name} attempted to rob {target.name}, but it failed. They lost {rob_penalty} electricity as a penalty.",
            color=0xff0000
        )
        await ctx.send(embed=embed)




token = os.environ.get("TOKEN")
bot.run(os.getenv('TOKEN'))
