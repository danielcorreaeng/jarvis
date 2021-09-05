# Jarvis

A Personal Assistant for Linux and Windows in developed.
The objective is store automation codes in the database and execute them with associated tags.

## Authors

 **danielcorreaeng** 

See also the list of [contributors](contributors.md) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Help
Try:

    python Jarvis.py help
 
Result:

	Hum... Let me try :
         <tag0> <tag1> : i execute the code what it have <tag0> <tag1>.
         record <tag0> <tag1> : i try open editor code and i will record it with tags.
         read <file> <tag0> <tag1> : give me a file and i record with <tag0> <tag1>.
         write <file> <tag0> <tag1> : i save the code in <file>.
         list <tag0> : i try find in my memory <tag0>.
         find <tag0> : i try find in my memory <tag0> and describes.
         copy <base> <tag0> : i copy <tag0> to <base>.
         forget <tag0> : i forget <tag>... I think this.
         <tag0> <tag1> -base=<base> : i execute the code what it have tags from <base>.
         <tag0> <tag1> -display=true : i execute the code using the program display.
         <tag0> <tag1> -program=<program> : i execute the code using other program.
         mybot blablabla. : i will speek with you.
         
In short, you create a new command (default editor spyder3) with **Jarvis.py create tag** and then run it with **Jarvis.py tag**

Chatbot is a command-enabled microservice in default base.
    
    python Jarvis.py chatbot -base=services

It use the terminal as flask microservice. Use **other terminal** to chat like exemple.

    python Jarvis.py mybot oi!
    python Jarvis.py mybot [learn] Tchau [answer] Bye!
    python Jarvis.py mybot Tchau

## Instalation

It has been tested with Python 3.6.8 and Python 3.7.10.

### Windows

Best practices that I used to maximize application automations will be demonstrated.

For instalation, you will install the requirements **in path of Jarvis**.

    pip install -r requirements.txt

Test application.

    python Jarvis.py find
    
You can create a **bat file** to make the commands easier. Something like this command. 

    @echo off
    python C:\Jarvis\Jarvis.py %*

Save this file with **Jarvis.bat in C:\Windows\System32\ .** You need reboot your system. After that enter in **windows prompt command and test**.

    Jarvis find

If you want work with services and chatbots, i suggest you put a **bat file** in your **%AppData%\Microsoft\Windows\Start Menu\Programs\Startup** . Something like this command.

    python C:\Jarvis\jarvis.py controller -base=services
 
It will open **jarvis service controller** and you can add services like chatbot and logger and others. By default it will run the services **chatbot -base=services** and **datalogger -base=services**. You can edit it.

    Jarvis record controller -base=services
    
Or put in **config.ini** in section **CriticalServices** other jarvis services commands like it.

    [CriticalServices]
    bla1=datalogger -base=services
    bla2=calc
    bla3=test -base=test
    
The service in **%AppData%\Microsoft\Windows\Start Menu\Programs\Startup** will start in next restart system.

Try after that ask with your bot in your **windows prompt command**

    Jarvis mybot oi!
    
I use to name my bots. For that I create a **bat file** like to this one.

    @echo off
    python C:\Jarvis\Jarvis.py mybot %*

I save this file with **BOTNAME.bat in C:\Windows\System32\ .** You need reboot your system. After that enter in **windows prompt command and test**.
    
    BOTNAME oi!

To teach him/her something new, use command

    BOTNAME [learn] Ola! [answer] oioi!
    
Have fun!!! =)

## config.ini example

config.ini example

    [Parameters]
    PyCommand=python
    PyScripter=code
    BotIp=192.168.15.49:8805

    [CriticalServices]


    [Telegram]
    token=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    alloweduser=@user
