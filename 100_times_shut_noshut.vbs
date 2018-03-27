#$language = "VBScript"
#$interface = "1.0"

crt.Screen.Synchronous = False

' This automatically generated script may need to be
' edited in order to work correctly.
Function ToUnixTime(strTime, intTimeZone)       
    	If IsEmpty(strTime) or Not IsDate(strTime) Then strTime = Now       
    	If IsEmpty(intTimeZone) or Not isNumeric(intTimeZone) Then intTimeZone = 0       
     	ToUnixTime = DateAdd("h",-intTimeZone,strTime)       
     	ToUnixTime = DateDiff("s","2018-1-16 0:0:0", ToUnixTime)       
End Function

Function Act_slot_shut_no_shut(intSlot,intStart,intEnd)
	crt.Screen.Send "conf" & chr(13)
	For i = intStart To intEnd
	crt.Screen.Send "int" & chr(9) & "e"&intSlot&"/" & i & chr(13)
	crt.Screen.Send "shu" & chr(9) & chr(13)
	crt.Screen.Send chr(13)
	crt.Screen.Send "no shu" & chr(9) & chr(13)
	crt.Screen.Send "exit" & chr(13)
	Next
End Function

Sub Main
	Tbegin = Now
	TlastEnd = Now
	T3 = ToUnixTime(TlastEnd,0)
	num = 3
	do while num > 0
	    T1 = Now
	    T2 = ToUnixTime(T1,0)
	    if T2 - T3 > 5 then
	        crt.Screen.Send T1&chr(13)&T2& chr(13)
	        Act_slot_shut_no_shut 1,1,8
		Act_slot_shut_no_shut 2,1,16
		Act_slot_shut_no_shut 4,1,16
	        num = num - 1
		T3 = T2
	    end if
	loop

End Sub
