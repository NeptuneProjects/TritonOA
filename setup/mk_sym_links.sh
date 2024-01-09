# *** Set AT_PATH to the directory containing Acoustics Toolbox (AT) ***
AT_PATH = <path to AT> # <-- Set the path here
echo $AT_PATH
ln -s $AT_PATH/Kraken/bounce.exe /usr/local/bin/bounce.exe
ln -s $AT_PATH/Kraken/kraken.exe /usr/local/bin/kraken.exe
ln -s $AT_PATH/Kraken/krakenc.exe /usr/local/bin/krakenc.exe
#ln -s $AT_PATH/Kraken/bellhop3d.exe /usr/local/bin/bellhop3d.exe
#ln -s $AT_PATH/Kraken/bellhop.exe /usr/local/bin/bellhop.exe
ln -s $AT_PATH/KrakenField/field.exe /usr/local/bin/field.exe
ln -s $AT_PATH/KrakenField/field3d.exe /usr/local/bin/field3d.exe
#ln -s $AT_PATH/KrakenField/scooter.exe /usr/local/bin/scooter.exe
#ln -s $AT_PATH/KrakenField/sparc.exe /usr/local/bin/sparc.exe
ln -s $AT_PATH/Bellhop/bellhop.exe /usr/local/bin/bellhop.exe
ln -s $AT_PATH/Bellhop/bellhop3d.exe /usr/local/bin/bellhop3d.exe
ln -s $AT_PATH/Scooter/scooter.exe /usr/local/bin/scooter.exe
ln -s $AT_PATH/Scooter/sparc.exe /usr/local/bin/sparc.exe
