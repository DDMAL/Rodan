# runs the commands in new terminal tabs 
osascript -e 'tell application "iTerm" to activate' -e 'tell application "System Events" to tell process "iTerm" to keystroke "n" using command down' -e 'tell application "System Events" to tell process "iTerm" to keystroke "cd ~/Desktop/Rodan && make run_arm
"' 
#sleep 30 
osascript -e 'tell application "iTerm" to activate' -e 'tell application "System Events" to tell process "iTerm" to keystroke "d" using command down' -e 'tell application "System Events" to tell process "iTerm" to keystroke "cd ~/Desktop/Rodan && docker-compose exec rodan-main /run/start
"' 
#sleep 60 
osascript -e 'tell application "iTerm" to activate' -e 'tell application "System Events" to tell process "iTerm" to keystroke "d" using command down' -e 'tell application "System Events" to tell process "iTerm" to keystroke "cd ~/Desktop/Rodan && docker-compose exec celery /run/start
"' 
osascript -e 'tell application "iTerm" to activate' -e 'tell application "System Events" to tell process "iTerm" to keystroke "d" using command down' -e 'tell application "System Events" to tell process "iTerm" to keystroke "cd ~/Desktop/Rodan && docker-compose exec py3-celery /run/start
"' 
echo "######### DEPLOYED #########"

# wait for the key q and terminate and close all the tabs if q is entered 
echo "enter q to terminate the process"
read key
if [[ $key = q ]] 
then
    osascript -e 'tell application "iTerm" to activate' -e 'tell application "System Events" to tell process "iTerm" to keystroke "2" using command down' -e 'tell application "System Events" to tell process "iTerm" to keystroke "w" using command down' 
    osascript -e 'tell application "iTerm" to activate' -e 'tell application "System Events" to tell process "iTerm" to keystroke "w" using command down'
    osascript -e 'tell application "iTerm" to activate' -e 'tell application "System Events" to tell process "iTerm" to keystroke "w" using command down'
    osascript -e 'tell application "iTerm" to activate' -e 'tell application "System Events" to tell process "iTerm" to keystroke "w" using command down'
    printf "\nQuitting from the program\n"
fi
break

