#clearing .log files
if [[ X$1 != X ]]; then
    eosrm /store/user/xinlong/$1/*output.log
fi
rm *Validation*output.log
rm *Signal*output.log
rm *Control*output.log
rm *2022*output.log
rm *2023*output.log
rm *2024*MC*output.log
rm *2024*Data*output.log
rm *output.log
