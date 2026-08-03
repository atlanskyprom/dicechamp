# Dicechamp - The dice roller for Champions 
import discord
import random
import math
import logging
import time
import os
import subprocess

# Variables
char_dict={
        "discord_username1":"Game Master",
        "discord_username2":"character_name2",
        "discord_username3":"character_name3",
        "discord_username4":"character_name4",
        "discord_username5":"character_name5"
        }


# Configure logging
logging.basicConfig(level=logging.INFO, filename='/path/to/dicechamp.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')
logging.info('Starting service at ' + str(time.asctime())) 

with open('/path/to/.dicechamp_discord.key', 'r') as env_file:
    discord_key = env_file.read().rstrip()

# Configure Discord Client
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    logging.info(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("Hello! To learn about my syntax, type $help.")
        logging.info(str(time.asctime()) + f' {message.author} typed ' + message.content)

    if message.content.startswith('$help'):
        logging.info(str(time.asctime()) + f' {message.author} typed ' + message.content)
        send_txt=("**$hello** - Greet Dicechamp\n" +  
                "*Basic Rolls*\n" +
                "**$roll** - Roll 1d6\n" + 
                "**$rollh** - Roll 1/2d6\n" + 
                "**$roll[#]** - Roll # d6, i.e. $roll5\n" + 
                "*Normal Damage Rolls*\n" +
                "**$dam** - Normal 1d6 Damage roll\n" + 
                "**$damh** - Normal 1/2d6 damage roll\n" + 
                "**$dam[#][h]** - Normal Damage with # dice, optional h for adding 1/2d6 roll\n" + 
                "*Killing Damage Rolls*\n" +
                "**$kill** - Killing 1d6 damage roll\n" + 
                "**$kill[#]** - Killing #d6 damage roll\n" + 
                "**$kill[#][s][#]** - Killing damage with # dice, optional s for adding # to STUN multiplier\n" + 
                "*Attack Rolls*\n" +
                "**$atk[ocv]** - Attack roll, takes attacker's OCV and calculates the DCV hit\n" + 
                "*Other*\n" +
                "**$suc** - Success Roll\n" + 
                "**$tm[distance]** - Turn Mode\n" + 
                "**$hitloc** - Roll Hit Location\n")  
        embed = discord.Embed(
            colour=discord.Colour.yellow(),
            description=(send_txt),
            title="Available Commands"
        )
        await message.channel.send(embed=embed)

    if message.content.startswith('$suc'):
        logging.info(str(time.asctime()) + f' {message.author} typed ' + message.content)
        # Initialize variables
        send_txt=""
        total_rolled=0
        number_dice_int=3
        roll_seq=1
        # Make the rolls
        for i in range(number_dice_int):
           rolled=random.randint(1,6)
           total_rolled=total_rolled+rolled
           send_txt = send_txt + ("`" + str(roll_seq) + ": " + str(rolled) + "`\n")
           roll_seq=roll_seq+1
        send_txt = send_txt + "\n**Total**\n" + str(total_rolled) +  " points"
        embed = discord.Embed(
            colour=discord.Colour.dark_teal(),
            description=(send_txt),
            #title="Success Roll from " + str(message.author) 
            title="Success Roll from " + str(char_dict[str(message.author)])
        )
        await message.channel.send(embed=embed)

    if message.content.startswith('$atk'):
        logging.info(str(time.asctime()) + f' {message.author} typed ' + message.content)
        # Initialize variables
        total_rolled=0
        number_dice_int=3
        roll_seq=1
        send_txt=""
        # Assign text of message to orig_cmd
        orig_cmd=message.content
        # Assign command options to ocv
        ocv=str.replace(orig_cmd, '$atk', '')
        if ocv=="":
            send_txt="Please include an OCV value in the command, such as $atk10"
            await message.channel.send(send_txt)
        else:
           # Banner
           # Make the rolls
           for i in range(number_dice_int):
              rolled=random.randint(1,6)
              total_rolled=total_rolled+rolled
              send_txt = send_txt + ("`" + str(roll_seq) + ": " + str(rolled) + "`\n")
              roll_seq=roll_seq+1
           dcv=(int(ocv)+ 11)-total_rolled
           send_txt = send_txt + ("`OCV " + str(ocv) + " + 11, - " + str(total_rolled) + " = DCV: " + str(dcv) + "`\n")
           send_txt = send_txt + "\n**DCV attacker can hit: " + str(dcv) + "**\n"
           embed = discord.Embed(
               colour=discord.Colour.dark_red(),
               description=(send_txt),
               title="Attack Roll from " + str(char_dict[str(message.author)])
           )
           await message.channel.send(embed=embed)

    if message.content.startswith('$tm'):
        logging.info(str(time.asctime()) + f' {message.author} typed ' + message.content)
        # Initialize variables
        curr_turn_mode=0
        send_txt=""
        # Assign text of message to orig_cmd
        orig_cmd=message.content
        # Assign command options to ocv
        distance=str.replace(orig_cmd, '$tm', '')
        if distance=="":
            send_txt="Please include a distance value in the command, such as $tm10"
            await message.channel.send(send_txt)
        else:
           # Calc the Current Turn Mode 
           curr_turn_mode=int(distance)/5
           send_txt = send_txt + "\n**Can turn again in " + str(curr_turn_mode) + "m**\n"
           embed = discord.Embed(
               colour=discord.Colour.dark_red(),
               description=(send_txt),
               title="Turn Mode for " + str(char_dict[str(message.author)])
           )
           await message.channel.send(embed=embed)


    if message.content.startswith('$roll'):
        logging.info(str(time.asctime()) + f' {message.author} typed ' + message.content)
        # Initialize variables
        total_rolled=0
        number_dice_int=0
        send_txt=""
        # Assign text of message to orig_cmd
        orig_cmd=message.content
        # Assign command options to number_dice
        number_dice=str.replace(orig_cmd, '$roll', '')
        # Banner
        # If nothing entered besides the command, defaults to 1 die
        if number_dice=="":
           number_dice_int=1
        # If last character is an "h", make the roll and calc the results
        elif number_dice[-1]=="h":
           # Strip the "h" character from the end of number_dice
           number_dice=number_dice[:-1]
           # Roll 1/2d6 to rolled_halved
           rolled_all=random.randint(1,6)
           rolled_halved=(rolled_all * .5)
           # Round up to rolled_rounded
           rolled_rounded=int(math.ceil(rolled_halved))
           # Add to the total_rolled
           total_rolled=rolled_rounded
           # Send results of 1/2d6 STUN and BODY
           send_txt = send_txt + ("`1/2d6 roll: " + str(rolled_all) + ", Haved: " + str(rolled_halved) + ". Rounded up: +" + str(rolled_rounded) + "`\n")
           # If there was a number of dice specified along with "h", assign that number to number_dice_int
           if number_dice != "":
               number_dice_int = int(number_dice)
        # If number of dice passed, create number_dice_int
        else:
           number_dice_int = int(number_dice)
        # If the number of dice determine above is >20, then make it 20. 
        if number_dice_int>20:
           number_dice_int=20
        # Roll dice "number_dice_int" times, adding to total_rolled
        for i in range(number_dice_int):
           rolled=random.randint(1,6)
           # Add new roll to total_rolled
           total_rolled=total_rolled+rolled
           roll_seq=i+1
           # Send roll result
           send_txt = send_txt + ("`" + str(roll_seq) + ": " + str(rolled) + "`\n" )
        send_txt = send_txt + ("\n**Total**\n " + str(total_rolled)+ " points")
        # Send Total
        embed = discord.Embed(
                colour=discord.Colour.green(),
                description=(send_txt),
                title="**" + str(char_dict[str(message.author)]) + "** rolls the dice!"
        )
        await message.channel.send(embed=embed)

    if message.content.startswith('$dam'):
        logging.info(str(time.asctime()) + f' {message.author} typed ' + message.content)
        # Initialize variables
        total_stun=0
        total_body=0
        number_dice_int=0
        send_txt=""
        # Assign text of message to orig_cmd
        orig_cmd=message.content
        # Assign command options to number_dice
        number_dice=str.replace(orig_cmd, '$dam', '')
        # Banner
        # If nothing entered besides the command, defaults to 1 die
        if number_dice=="":
           number_dice_int=1
        # If last character is an "h", make the roll and calc the results
        elif number_dice[-1]=="h":
           # Strip the "h" character from the end of number_dice
           number_dice=number_dice[:-1]
           # Roll 1/2d6 to rolled_halved
           rolled_all=random.randint(1,6)
           rolled_halved=(rolled_all * .5)
           # Round up to rolled_rounded
           rolled_rounded=int(math.ceil(rolled_halved))
           # Add results to total_stun
           total_stun=rolled_rounded
           # +1 BODY for rolls 4-6
           if rolled_all > 3:
               total_body=1
           # Send results of 1/2d6 STUN and BODY
           send_txt = send_txt +  ("`1/2d6 roll: " + str(rolled_all) + ", Haved: " + str(rolled_halved) + ". Rounded up: +" + str(rolled_rounded) + " STUN, +" + str(total_body) + " BODY`\n")
           # If there was a number of dice specified along with "h", assign that number to number_dice_int
           if number_dice != "":
               number_dice_int = int(number_dice)
        else:
           # If the command has a suffix, and does not end in "h", then the suffix is the noumber of dice to roll
           number_dice_int = int(number_dice)
        # If the number of dice determine above is >20, then make it 20. 
        if number_dice_int>20:
           number_dice_int=20
        # Roll dice "number_dice_int" times, adding to total_stun
        for i in range(number_dice_int):
           rolled=random.randint(1,6)
           total_stun=total_stun+rolled
           # Determine BODY based on rolled
           if rolled==1:
             rolled_body="0"
           elif rolled==6:
             rolled_body="2"
             total_body=total_body+2
           else:
             rolled_body="1"
             total_body=total_body+1
           roll_seq=i+1
           send_txt = send_txt + ("`" + str(roll_seq) + "-STUN: " + str(rolled) + " / " + "BODY: " + rolled_body + "`\n")
        send_txt = send_txt + ("\n**Total**\n**STUN**: " + str(total_stun) + "\n" + "**BODY**: " + str(total_body) + "\n\n")
        # Knockback
        send_txt = send_txt + ("**Knockback**\n")
        kbroll1=random.randint(1,6)
        kbroll2=random.randint(1,6)
        kbtotal=kbroll1 + kbroll2
        send_txt = send_txt + ("`1-KB: " + str(kbroll1) + "`\n")
        send_txt = send_txt + ("`2-KB: " + str(kbroll2) + "`\n")
        kbresult=total_body-kbtotal
        send_txt = send_txt + ("\nKB Rolls: " + str(kbtotal) + "\nKB Calc: " + str(kbresult))
        if kbresult<0:
            kbdist=0
            kbunits="m"
        elif kbresult==0:
            kbdist=""
            kbunits="prone"
        else:
            kbdist=kbresult*2
            kbunits="m"
        send_txt = send_txt + ("\n**KB Distance: " + str(kbdist) + str(kbunits) + "**")
        # Send Completed Message
        embed = discord.Embed(
                colour=discord.Colour.orange(),
                description=(send_txt),
                title="**Damage Roll from " + str(char_dict[str(message.author)]) + "!**"
        )
        await message.channel.send(embed=embed)
    
    if message.content.startswith('$kill'):
        logging.info(str(time.asctime()) + f' {message.author} typed ' + message.content)
        # Initialize variables
        stun_add=0
        total_stun=0
        total_body=0
        number_dice_int=0
        send_txt=""
        # Assign text of message to orig_cmd
        orig_cmd=message.content
        # Assign command options to number_dice
        number_dice=str.replace(orig_cmd, '$kill', '')
        # Roll to determine the STUN multiplier as stun_mult
        stun_mult_roll=random.randint(1,6)
        stun_mult_raw=(stun_mult_roll * .5)
        # Round up to stun_mult_rounded
        stun_mult=int(math.ceil(stun_mult_raw))
        # Banner
        # If nothing entered besides the command, defaults to 1 die
        if number_dice=="":
           number_dice_int=1
        # If second to last character is an "s", then we have a STUN modifier
        #elif number_dice[-2]=='s':
        elif len(number_dice) >1 :
           if number_dice[-2]=='s':
              # Get the stun_multiplier
              stun_add=number_dice[-1]
              send_txt = send_txt + ("STUN Modiifer Add " + stun_add + "\n\n")
              # Strip the "s*" characters from the end of number_dice
              number_dice=number_dice[:-2]
              # Make number_dice_int
              number_dice_int = int(number_dice)
              if number_dice != "":
           	    number_dice_int = int(number_dice)
           else:
                number_dice_int = int(number_dice)
        else:
           # If the command has a suffix, and does not have a "s", then the suffix is the number of dice to roll
           number_dice_int = int(number_dice)
           # If the number of dice determined above is >20, then make it 20. 
        if number_dice_int>20:
           number_dice_int=20
        # Roll dice "number_dice_int" times, adding to total_body
        for i in range(number_dice_int):
           rolled=random.randint(1,6)
           total_body=total_body+rolled
           roll_seq=i+1
           send_txt = send_txt + ("`" + str(roll_seq) + "-BODY: " + str(rolled) + "`\n")
        # Multiply total BODY by STUN modifier to determine total STUN 
        stun_add_int = int(stun_add)
        stun_mult_add = stun_mult + stun_add_int
        total_stun=total_body*stun_mult_add
        # Send STUN calc summary
        send_txt = send_txt + ("`STUN roll: " + str(stun_mult_roll) + ", STUN Multiplier: (" + str(stun_mult) + " + " + str(stun_add) + ") X " + str(total_body) + " = +" + str(total_stun) + " STUN`\n")
        send_txt = send_txt + "\n**Total**\nSTUN: " + str(total_stun) + "\n" + "BODY: " + str(total_body) + "\n"
        # Send Total STUN and BODY
        embed = discord.Embed(
                colour=discord.Colour.red(),
                description=(send_txt),
                title="**Killing Damage Roll from " + str(char_dict[str(message.author)]) + "!**"
        )
        await message.channel.send(embed=embed)

    if message.content.startswith('$hitloc'):
        logging.info(str(time.asctime()) + f' {message.author} typed ' + message.content)
        # Initialize variables
        number_dice_int=3
        total_rolled=0
        hand=""
        handed=""
        send_txt="**Rolls**: "
        # Make the rolls
        for i in range(number_dice_int):
           rolled=random.randint(1,6)
           total_rolled=total_rolled + rolled
           send_txt = send_txt + str(rolled) + ", " 
        send_txt = send_txt + "total: " + str(total_rolled) + "\n"
        if total_rolled < 6:
                hit_location="Head"
                STUNx="x5"
                N_STUN="x2"
                BODYx="x2"
                OCV="-8"
        if total_rolled == 6:
                hit_location="Hand"
                STUNx="x1"
                N_STUN="x.5"
                BODYx="x.5"
                OCV="-6"
                handed="y"
        if total_rolled in [7,8]:
                hit_location="Arm"
                STUNx="x2"
                N_STUN="x.5"
                BODYx="x.5"
                OCV="-5"
                handed="y"
        if total_rolled == 9:
                hit_location="Shoulder"
                STUNx="x3"
                N_STUN="x1"
                BODYx="x1"
                OCV="-5"
                handed="y"
        if total_rolled in [10,11]:
                hit_location="Chest"
                STUNx="x3"
                N_STUN="x1"
                BODYx="x1"
                OCV="-3"
        if total_rolled == 12:
                hit_location="Stomach"
                STUNx="x4"
                N_STUN="x1.5"
                BODYx="x1"
                OCV="-7"
        if total_rolled == 13:
                hit_location="Vitals"
                STUNx="x4"
                N_STUN="x1.5"
                BODYx="x2"
                OCV="-8"
        if total_rolled == 14:
                hit_location="Thigh"
                STUNx="x2"
                N_STUN="x1"
                BODYx="x1"
                OCV="-4"
                handed="y"
        if total_rolled in [15,16]:
                hit_location="Leg"
                STUNx="x2"
                N_STUN="x.5"
                BODYx="x.5"
                OCV="-6"
                handed="y"
        if total_rolled in [17,18]:
                STUNx="x1"
                N_STUN="x.5"
                BODYx="x.5"
                OCV="-8"
                handed="y"
        if handed=="y":
             handroll=random.randint(1,6)
             if handroll < 4:
                 hand="left"
             else:
                 hand="right"
             hit_location=(hit_location + " (" + hand + ")")
        send_txt = send_txt + "**Hit Location**: " + hit_location + "\n" + "**STUNx**: " + STUNx + "\n**N STUN**: " + N_STUN + "\n**BODYx**: " + BODYx + "\n**OCV**: " + OCV + "\n"
        embed = discord.Embed(
                colour=discord.Colour.green(),
                description=(send_txt),
                title="**Hit Location roll from " + str(message.author) + "!**"
        )
        await message.channel.send(embed=embed)



