# discli
discli is a curses-based Discord client written in Python using [discord.py](https://github.com/Rapptz/discord.py)  
discli is in *very* early beta. It's super unstable and crashes all the time. Tons on features are missing. Please report and crashes an oddities on the [issues](https://github.com/giantfroje/discli/issues) page.

## WARNING
Using any form of code to control a non-bot Discord account breaks [Discord Community Guidelines](https://discord.com/guidelines). Use at your own risk, I am not responsible of you get banned ([License](https://github.com/giantfroje/discli/blob/main/LICENSE)).

## Security
Is discli safe? I don't know, look at the source.  

## Installation
1. Clone the repository 
```
git clone https://github.com/giantfroje/discli.git
```

2. Install requirements: 
```
pip install -r requirements.txt
```

3. Run `discli.py`: 
```
py discli.py
```

4. Input your [Discord token](https://discordhelp.net/discord-token)
5. Create a password (Note: this doesn't have to be your Discord password)

That's it!

## Usage
discli is completely keyboard-controlled.  
The controls are pretty intuitive, I'll get around to wrting a better description of the controls soon™

### Shortcuts
`Shift+Tab` - Toggle "console mode"

### Commands
`quit` - Exit discli - Alias(es): `q`  
`servers` - Switch server - Alias(es): `s` `guilds` `g`  
`channels` - Switch channels - Alias(es): `c`  
`echo <message>` - Send message (why?)
