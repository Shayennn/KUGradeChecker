# KUGradeChecker

This is bot for checking grade updating via Kasetsart University Student grade system. It'll notify by Line Notify.

## Usage

Clone this repo by

``` bash
git clone --branch NisitApp https://github.com/Shayennn/KUGradeChecker.git
```

Then run this command to install require packages.

``` bash
pip3 install -r requirements.txt
```

### Testing

``` bash
python3 check_by_nisitku.py
```

The program will ask you for Username and Password. Please feel free and enter your Nontri Account Username, Password.

Then you'll see your current grade.

### Auto checking

``` bash
python3 autocheck_group.py
```

For the first time. Please enter your Nontri Account Username, Password and your Line Notify Dev Token. (From [LINE Notify](https://notify-bot.line.me/my/))

Then you must to set cronjob or anything else like it.

#### Crontab setting

This is an example of setting crontab for auto update grade every 2 mins.

``` bash
crontab -e
```

Then enter this to the end of file.

``` text
*/2 * * * * (cd PATH_TO_KUGradeChecker&&timeout 30 python3 autocheck_group.py >> check.log)
```

## Minimum Requirement

May be very low. (I didn't massure.)

## License

สงวนลิขสิทธิ์ทั้งหมดโดย นาย พิชวัชร ลัคนาธิติ
อนุญาตการใช้งานที่ไม่ใช่เพื่อการค้า โดยมีเงื่อนไขว่า ไม่อนุญาตให้บุคคลอื่นที่ไม่ใช่เจ้าของ Nontri Account นั้น ๆ ใช้งาน ไม่ว่ากรณีใดก็ตาม (นาย A ต้องใช้บัญชีนาย A เพื่อประโยชน์แห่งนาย A คนเดียวเท่านั้น)
