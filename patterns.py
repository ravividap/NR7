opend0= OpenSession(0,0);
opend1= OpenSession(0,1);
opend2= OpenSession(0,2);
opend3= OpenSession(0,3);
opend4= OpenSession(0,4);
opend5= OpenSession(0,5);

highd0= HighSession(0,0);
highd1= HighSession(0,1);
highd2= HighSession(0,2);
highd3= HighSession(0,3);
highd4= HighSession(0,4);
highd5= HighSession(0,5);

lowd0= LowSession(0,0);
lowd1= LowSession(0,1);
lowd2= LowSession(0,2);
lowd3= LowSession(0,3);
lowd4= LowSession(0,4);
lowd5= LowSession(0,5);

closed0= CloseSession(0,0);
closed1= CloseSession(0,1);
closed2= CloseSession(0,2);
closed3= CloseSession(0,3);
closed4= CloseSession(0,4);
closed5= CloseSession(0,5);

#volatility patters

	case 1 = absvalue(opend1-closed1)<0.5*(highd1-lowd1)  ;  
	case 2 = absvalue(opend1-closed5)<0.5*(highd5-closed1)  ;  
	case 3= absvalue(opend5-closed1) <0.5*(maxlist(highd1,highd2,highd3,highd4,highd5) - minlist(lowd1,lowd2,lowd3,lowd4,lowd5))  ;
	
#Directional patterns include two time frames	
	case 4 = ((highd0-opend0)> ((highd1-opend1)*1))  ; 
	case 5 = ((highd0-opend0)> ((highd1-opend1)*1.5)) ; 
	case 6 =  ((opend0-lowd0)> ((opend1-lowd1)*1)) ;
	case 7 =  ((opend0-lowd0)> ((opend1-lowd1)*1.5))  ; 
	case 8=  closed1>closed2 and closed2>closed3 and closed3>closed4; 
	case 9 =  closed1<closed2 and closed2<closed3 and closed3<closed4;
	case 10 =  highd1>highd2 and lowd1>lowd2;
	case 11 =  highd1<highd2 and lowd1<lowd2;
	
# Range Expansion/Compression intraday
	case 12 = ((highd0>(lowd0+lowd0*0.75/100)));
	case 13 = ((highd0<(lowd0+lowd0*0.75/100)));

# Don;t know what to call ;)
	case 14 = (closed1>closed2);
	case 15 = (closed1<closed2);
	case 16 = (closed1<opend1);
	case 17 = (closed1>opend1);
	case 18 = ((closed1<(closed2-closed2*0.5/100)));
	case 19 = ((closed1>(closed2+closed2*0.5/100)));

#Trend
	case 20 = (highd0>(highd1));
	case 21 = (highd1>highd5);
	case 22 =(lowd0<lowd1);
	case 23 =(lowd1<lowd5);
	case 24=(highd1> highd2) and (highd1> highd3) and (highd1> highd4); 
	case 25=(highd1< highd2) and (highd1< highd3) and (highd1< highd4); 
	case 26 =((lowd1 < lowd2) and (lowd1 < lowd3) and (lowd1 < lowd4));
	case 27 =((lowd1 > lowd2) and (lowd1 > lowd3) and (lowd1 > lowd4));
	
	case 28=(closed1>closed2 and closed2>closed3 and opend0>closed1);
	case 29 =(closed1<closed2 and closed2<closed3 and opend0<closed1);
	case 30 =((highd1-closed1)<0.20*(highd1-lowd1));
	case 31=((closed1-lowd1)<0.20*(highd1-lowd1));
	case 32 =(opend0<lowd1 or opend0>highd1);
	case 33=((opend0<(closed1-closed1*0.5/100)));
	case 34 =((opend0>(closed1+closed1*0.5/100)));
	case 35 =(highd0<highd1 and lowd0>lowd1);
	
#Vol contraction
	case 36=(highd1-lowd1)< (((highd2-lowd2)+ (highd3-lowd3))/3);
	case 37 =(highd1-lowd1)< (highd2-lowd2) and (highd2-lowd2) < (highd3-lowd3); 

#Inside bar/Outside bar
	case 38=(highd2>highd1 and lowd2<lowd1);
	case 39 =(highd1<highd2 or lowd1>lowd2);
	case 40 =(highd2<highd1 and lowd2>lowd1);


