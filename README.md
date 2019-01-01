# KUGradeChecker
This is bot for checking grade updating via Kasetsart University Student grade system. It'll notify by Line Notify.

## Usage
Clone this repo by
```
git clone https://github.com/Shayennn/KUGradeChecker.git
```
Then run this command to install require packages.
```
pip3 install -r requirements.txt
```
### Testing
```
python3 main.py
```
The program will ask you for Username and Password. Please feel free and enter your Nontri account.

Then you'll see your current grade.

### Auto checking
```
python3 autocheck.py
```
For the first time. Please enter your Nontri account and your Line Notify Dev Token. (From [LINE Notify](https://notify-bot.line.me/my/))

Then you must to set cronjob or anything else like it.

#### Crontab setting
This is an example of setting crontab for auto update grade every 2 mins.
```
crontab -e
```
Then enter this to the end of file.
```
*/2 * * * * cd PATH_TO_KUGradeChecker&&timeout 30 python3 autocheck.py
```
# Minimum Requirement
* Operating system that can install Tensorflow(Python)
* 512MB of Memory

# License
All right reserved