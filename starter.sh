# runs the commands in new terminal tabs you have to open a new separate window of iterm to start with 
osascript -e 'tell application "iTerm" to activate' -e 'tell application "System Events" to tell process "iTerm" to keystroke "t" using command down' -e 'tell application "System Events" to tell process "iTerm" to keystroke "cd ~/Desktop/Rodan && make run_arm
"' 
sleep 30 
osascript -e 'tell application "iTerm" to activate' -e 'tell application "System Events" to tell process "iTerm" to keystroke "d" using command down' -e 'tell application "System Events" to tell process "iTerm" to keystroke "cd ~/Desktop/Rodan && docker-compose exec rodan-main /run/start
"' 
sleep 30 
osascript -e 'tell application "iTerm" to activate' -e 'tell application "System Events" to tell process "iTerm" to keystroke "d" using command down' -e 'tell application "System Events" to tell process "iTerm" to keystroke "cd ~/Desktop/Rodan && docker-compose exec celery /run/start-celery
"' 
osascript -e 'tell application "iTerm" to activate' -e 'tell application "System Events" to tell process "iTerm" to keystroke "d" using command down' -e 'tell application "System Events" to tell process "iTerm" to keystroke "cd ~/Desktop/Rodan && docker-compose exec py3-celery /run/start-celery
"' 
echo "######### DEPLOYED #########"
sleep 20
osascript -e 'tell application "Google Chrome" to open location "http://localhost"'

# wait for the key q and terminate and close all the tabs if q is entered 
echo "enter q to terminate the process"
read key
while [[ $key != "q" ]]
do
  read key
done
if [[ $key = q ]] 
then
    osascript -e 'tell application "iTerm" to activate' -e 'tell application "System Events" to tell process "iTerm" to keystroke "2" using command down' -e 'tell application "System Events" to tell process "iTerm" to keystroke "w" using command down' 
    osascript -e 'tell application "iTerm" to activate' -e 'tell application "System Events" to tell process "iTerm" to keystroke "w" using command down'
    osascript -e 'tell application "iTerm" to activate' -e 'tell application "System Events" to tell process "iTerm" to keystroke "w" using command down'
    osascript -e 'tell application "iTerm" to activate' -e 'tell application "System Events" to tell process "iTerm" to keystroke "w" using command down'
    printf "\nQuitting from the program\n"
fi
# for the other features regarding the demands of your own environment you can modify the code above
# Author: Shahrad Mohammadzadeh
