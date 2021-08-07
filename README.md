# Global Growth Trend Timing Model

This project is an adaptation of the GTT models which I found [here](https://decodingmarkets.com/growth-trend-timing-with-us-stocks/). 

The original version of the GTT model combines price momentum and economic data. It can be described as follows: 

- Look at last month’s data for Real Retail and Food Services Sales (RRSFS) and US Industrial Production (INDPRO). If RRSFS and INDPRO are both lower than they were at the same time last year, a recession is signaled. (The reason we use last month’s data is that data is often restated and we want to avoid any form of lookahead bias).
- If a recession is signaled, next look at the 10-month price average for the SPY. If SPY is trading above its 10-month average then proceed to buy QQQ. (I used SPY as a proxy for the general market, and QQQ as a proxy for stocks with higher relative strength).
- If a recession is not signaled, go long QQQ. 
- If a recession is signaled and SPY is below it’s 10-month average, exit and wait for the model to exit the recessionary period.

The unemployment version of the GTT model combines price momentum with unemployment data:

- First, look at last month’s US unemployment rate (UNRATE). If last month’s unemployment rate is above the 12-month average unemployment rate, a recession is signaled. 
- If a recession is signaled, next look at the 10-month price average for the SPY. If SPY is trading above its 10-month average then proceed to buy QQQ. (I used SPY as a proxy for the general market, and QQQ as a proxy for stocks with higher relative strength)
- If a recession is not signaled, go long QQQ. 
- If a recession is signaled and SPY is below its 10-month average, exit and wait for the model to exit the recessionary period.

![stats](https://i.ibb.co/Ln9gdk6/Figure-2.png)

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Contact
If you would like to get in touch, my email is aleksandras.v.liauska@bath.edu.

## License
[GNU AGPLv3](https://choosealicense.com/licenses/agpl-3.0/)
