# Jarvis

A Personal Assistant for Linux and Windows in developed

## Authors

 **danielcorreaeng** 

See also the list of [contributors](contributors.md) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Help
Use Python 2.7

In windows, i use python portable and i create a Jarvis.bat with:

 @echo off
 C:\Jarvis\Python_Win\App\python.exe C:\Jarvis\Jarvis.py %*

and i save in C:\Windows\System32.

So...

C:\Users\Usuario>jarvis help
Hum... Let me try :
 <tag0> <tag1> : i execute the code what it have <tag0> <tag1>.
 record <tag0> <tag1> : i try open editor code and i will record it with tags.
 read <file> <tag0> <tag1> : give me a file and i record with <tag0> <tag1>.
 find <tag0> : i try find in my memory <tag0>.
 findAll <tag0> : i try find in my memory <tag0> and in my others lives too.
 forget <tag0> : i forget <tag>... I think this.

 <tag0> <tag1> -base=<base>: i execute the code what it have tags from <base>.
 <tag0> <tag1> -display=true: i execute the code using the program display.
 <tag0> <tag1> -program=<program>: i execute the code using other program.

 bot blablabla.: i will speek with you.

 