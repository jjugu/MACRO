#NoEnv
#SingleInstance force
SkinForm(Apply, A_ScriptDir . "\USkin.dll", A_ScriptDir . "\skin.msstyles")
OnExit, GetOut
gui, Color, FFFFFF
Gui, Add, GroupBox, x2 y30 w340 h350 CFF0000, 티켓팅 [ 처음시작 F1 ] [ 중지 / 재시작 F3 ]
Gui, Add, GroupBox, x352 y30 w340 h350 CFF0000, 취켓팅 [ 처음시작 F2 ] [ 중지 / 재시작 F3 ]
Gui, Add, CheckBox, x12 y50 w150 h20 v날짜사용, 날짜 회차 자동선택 사용
Gui, Add, Edit, x12 y80 w110 h20 v좌표xy1, 날 짜 좌 표
Gui, Add, Button, x252 y80 w80 h20 g좌표1, 좌표따기
Gui, Add, Edit, x12 y110 w110 h20 v좌표xy2, 회 차 좌 표
Gui, Add, Button, x252 y110 w80 h20 g좌표2, 좌표따기
Gui, Add, Edit, x12 y140 w110 h20 v좌표xy3, 다 음 단 계 좌 표
Gui, Add, Button, x252 y140 w80 h20 g좌표3, 좌표따기
Gui, Add, Button, x252 y170 w80 h20 g좌표4, 좌표따기
Gui, Add, Edit, x12 y170 w110 h20 v좌표xy4, 좌 석 범 위 ↖
Gui, Add, Edit, x12 y200 w110 h20 v좌표xy5, 좌 석 범 위 ↘
Gui, Add, Button, x252 y200 w80 h20 g좌표5, 좌표따기
Gui, Add, Edit, x12 y230 w110 h20 v좌표xy6, 선 택 완 료 좌 표
Gui, Add, Button, x252 y230 w80 h20 g좌표6, 좌표따기
Gui, Add, Edit, x12 y260 w230 h20 v색깔xy7, 좌 석 색 깔
Gui, Add, Button, x252 y260 w80 h20 g색깔7, 색깔따기
Gui, Add, Button, x2 y380 w340 h20 , 저장하기
Gui, Add, Button, x352 y380 w340 h20 , 불러오기
Gui, Add, Button, x2 y400 w690 h20 g자동, 자동 업데이트
Gui, Add, CheckBox, x12 y290 w80 h20 v1석, 1 석 잡 기
Gui, Add, CheckBox, x12 y310 w80 h20 v2석, 2 석 잡 기
Gui, Add, CheckBox, x12 y330 w80 h20 v3석, 3 석 잡 기
Gui, Add, CheckBox, x12 y350 w80 h20 v4석, 4 석 잡 기
Gui, Add, CheckBox, x362 y50 w110 h20 v구역o, 구역 있을시 선택
Gui, Add, CheckBox, x542 y50 w130 h20 v구역x, 구역 없을시 선택
Gui, Add, Edit, x362 y80 w230 h20 v색깔xy8, 1 구 역 좌 석 색 깔
Gui, Add, Button, x602 y80 w80 h20 g색깔8, 색깔따기
Gui, Add, Edit, x362 y110 w230 h20 v색깔xy9, 2 구 역 좌 석 색 깔
Gui, Add, Button, x602 y110 w80 h20 g색깔9, 색깔따기
Gui, Add, Edit, x362 y140 w110 h20 v좌표xy10, 선 택 완 료 좌 표
Gui, Add, Button, x602 y140 w80 h20 g좌표10, 좌표따기
Gui, Add, Edit, x362 y170 w110 h20 v좌표xy11, 1 좌 석 범 위 ↖
Gui, Add, Button, x602 y170 w80 h20 g좌표11, 좌표따기
Gui, Add, Edit, x362 y200 w110 h20 v좌표xy12, 1 좌 석 범 위 ↘
Gui, Add, Button, x602 y200 w80 h20 g좌표12, 좌표따기
Gui, Add, Edit, x362 y230 w110 h20 v좌표xy13, 2 좌 석 범 위 ↖
Gui, Add, Button, x602 y230 w80 h20 g좌표13, 좌표따기
Gui, Add, Edit, x362 y260 w110 h20 v좌표xy14, 2 좌 석 범 위 ↘
Gui, Add, Button, x602 y260 w80 h20 g좌표14, 좌표따기
Gui, Add, Edit, x362 y290 w150 h20 v취켓순간, 좌 석 잡 는 순 간 딜 레 이
Gui, Add, Text, x522 y290 w160 h20 , 빠른 PC 0 / 느린 PC 10~50
Gui, Add, Edit, x362 y320 w150 h20 v구역딜, 구 역 이 동 딜 레 이
Gui, Add, Text, x392 y350 w210 h20 , 빠른 PC 150~300 / 느린 PC 300~1000
Gui, Add, Text, x522 y320 w20 h20 , ↘
Gui, Add, Button, x612 y320 w70 h50 g취켓주의, 주 의 사 항
Gui, Add, Edit, x102 y290 w150 h20 v티켓순간, 좌 석 잡 는 순 간 딜 레 이
Gui, Add, Text, x102 y320 w60 h20 , 빠른 PC 0
Gui, Add, Button, x262 y290 w70 h50 g티켓주의, 주 의 사 항
Gui, Add, Text, x162 y320 w90 h20 , 느린 PC 10~50
Gui, Add, Edit, x102 y350 w70 h20 v오차, 오 차 범 위
Gui, Add, Text, x182 y350 w150 h20 , 평균 3 / 멜론티켓 20~25
Gui, Add, Edit, x132 y80 w110 h20 v1, 날 짜 좌 표
Gui, Add, Edit, x132 y110 w110 h20 v2, 회 차 좌 표
Gui, Add, Edit, x132 y140 w110 h20 v3, 다 음 단 계 좌 표
Gui, Add, Edit, x132 y170 w110 h20 v4, 좌 석 범 위 ↖
Gui, Add, Edit, x132 y200 w110 h20 v5, 좌 석 범 위 ↘
Gui, Add, Edit, x132 y230 w110 h20 v6, 선 택 완 료 좌 표
Gui, Add, Edit, x482 y140 w110 h20 v10, 선 택 완 료 좌 표
Gui, Add, Edit, x482 y170 w110 h20 v11, 1 좌 석 범 위 ↖
Gui, Add, Edit, x482 y200 w110 h20 v12, 1 좌 석 범 위 ↘
Gui, Add, Edit, x482 y230 w110 h20 v13, 2 좌 석 범 위 ↖
Gui, Add, Edit, x482 y260 w110 h20 v14, 2 좌 석 범 위 ↘
Gui, Add, Button, x472 y50 w60 h20 , 구역좌표
Gui, Show,, 통합 매크로
urldownloadtofile,http://white150.dothome.co.kr/buy.txt,구매자수.txt
IniRead,내용저장111, 구매자수.txt, 내용,1
guicontrol,,구매,%내용저장111%
FileDelete,구매자수.txt
return
GetOut:
GuiClose:
Gui, Hide
SkinForm(0)
ExitApp
return
SkinForm(Param1 = "Apply", DLL = "", SkinName = ""){
if(Param1 = Apply){
DllCall("LoadLibrary", str, DLL)
DllCall(DLL . "\USkinInit", Int,0, Int,0, AStr, SkinName)
}else if(Param1 = 0){
DllCall(DLL . "\USkinExit")
}
}
return
처음:
return
button구역좌표:
gui,2: Color, FFFFFF
Gui,2: Add, Edit, x12 y20 w120 h20 v좌표x1, 1 구 역 좌 표
Gui,2: Add, Edit, x142 y20 w120 h20 v좌표y1, 1 구 역 좌 표
Gui,2: Add, Edit, x12 y50 w120 h20 v좌표x2, 2 구 역 좌 표
Gui,2: Add, Edit, x142 y50 w120 h20 v좌표y2, 2 구 역 좌 표
Gui,2: Add, Button, x272 y20 w80 h20 g좌표111, 좌표따기1
Gui,2: Add, Button, x272 y50 w80 h20 g좌표222, 좌표따기2
Gui,2: Add, Button, x12 y80 w340 h20 , 이창을 닫지 마시오.
Gui,2: Show,,취켓팅 구역 정하기
gui,2: +alwaysontop +LastFound
return
F1::
SetControlDelay,-1
SetDefaultMouseSpeed,0
SetWinDelay,-1
SetMouseDelay,-1
SetBatchLines,-1
gui,submit,nohide
if(날짜사용=1)
{
gui,submit,nohide
sleep 200
mouseclick,left,%좌표xy1%,%1%,1
sleep 500
mouseclick,left,%좌표xy2%,%2%,1
sleep 500
mouseclick,left,%좌표xy3%,%3%,1
sleep 500
}
loop
{
if(1석=1)
{
PixelSearch, vx, vy ,%좌표xy4%,%4%,%좌표xy5%, %5%,%색깔xy7%, %오차%, Fast
if errorlevel=0
{
gosub, 1석잡다
sleep,50
mouseclick,left, %좌표xy6%,%6%,1
SoundPlay, %A_ScriptDir%\sound\띵동.mp3
sleep 500
send,{enter}
sleep 10
}
}
if(2석=1)
{
PixelSearch, vx, vy ,%좌표xy4%,%4%,%좌표xy5%, %5%,%색깔xy7%, %오차%, Fast
if errorlevel=0
{
gosub, 1석잡다
sleep 70
gosub, 1석잡다
sleep,50
mouseclick,left, %좌표xy6%,%6%,1
SoundPlay, %A_ScriptDir%\sound\띵동.mp3
sleep 500
send,{enter}
sleep 10
}
}
if(3석=1)
{
PixelSearch, vx, vy ,%좌표xy4%,%4%,%좌표xy5%, %5%,%색깔xy7%, %오차%, Fast
if errorlevel=0
{
gosub, 1석잡다
sleep 70
gosub, 1석잡다
sleep 70
gosub, 1석잡다
sleep,50
mouseclick,left, %좌표xy6%,%6%,1
SoundPlay, %A_ScriptDir%\sound\띵동.mp3
sleep 500
send,{enter}
sleep 10
}
}
if(4석=1)
{
PixelSearch, vx, vy ,%좌표xy4%,%4%,%좌표xy5%, %5%,%색깔xy7%, %오차%, Fast
if errorlevel=0
{
gosub, 1석잡다
sleep 70
gosub, 1석잡다
sleep 70
gosub, 1석잡다
sleep 70
gosub, 1석잡다
sleep,50
mouseclick,left, %좌표xy6%,%6%,1
SoundPlay, %A_ScriptDir%\sound\띵동.mp3
sleep 500
send,{enter}
sleep 10
}
}
}
return
F2::
SetControlDelay,-1
SetDefaultMouseSpeed,0
SetWinDelay,-1
SetMouseDelay,-1
SetBatchLines,-1
loop
{
gui,submit,nohide
PixelSearch, vx, vy ,%좌표xy11%,%11%,%좌표xy12%, %12%,%색깔xy8%, %오차%, Fast
if errorlevel=0
{
vX := vX+2
vY := vY+2
Mousemove,%vX%,%vY%
sleep,%취켓순간%
Mouseclick,left
sleep,%취켓순간%
Mouseclick,left,%좌표xy10%,%10%
SoundPlay, %A_ScriptDir%\sound\띵동.mp3
sleep 500
send,{enter}
sleep 10
}
gui,submit,nohide
if(구역o=1)
{
Gui,2:Submit,nohide
Mouseclick,left,%좌표x1%,%좌표y1%
}
gui,submit,nohide
if(구역x=1)
{
send,{down}
}
gui,submit,nohide
sleep %구역딜%
gui,submit,nohide
PixelSearch, vx, vy ,%좌표xy13%,%13%,%좌표xy14%, %14%,%색깔xy9%, %오차%, Fast
if errorlevel=0
{
vX := vX+2
vY := vY+2
Mousemove,%vX%,%vY%
sleep,%취켓순간%
Mouseclick,left
sleep,%취켓순간%
Mouseclick,left,%좌표xy10%,%10%
SoundPlay, %A_ScriptDir%\sound\띵동.mp3
sleep 500
send,{enter}
sleep 10
}
gui,submit,nohide
if(구역o=1)
{
Gui,2:Submit,nohide
Mouseclick,left,%좌표x2%,%좌표y2%
}
gui,submit,nohide
if(구역x=1)
{
send,{up}
}
gui,submit,nohide
sleep %구역딜%
}
return
F3::
pause
SoundBEEP
return
1석잡다:
gui,submit,nohide
PixelSearch, vx, vy ,%좌표xy4%,%4%,%좌표xy5%, %5%,%색깔xy7%, %오차%, Fast
if errorlevel=0
{
vX := vX+2
vY := vY+2
Mousemove,%vX%,%vY%
sleep,%티켓순간%
Mouseclick,left
}
return
button후원하기:
run, %A_ScriptDir%\textfile\ㄱ. 후원관련 필독.txt
return
button후기적립:
run, %A_ScriptDir%\textfile\ㄱ. 후기적립 필독.txt
return
button상담하기:
msgbox,,상담,카카오톡 [ @돌핀준이네 ] 우측하단 1:1 대화
return
button이벤트:
run, %A_ScriptDir%\textfile\ㄱ. 이벤트.txt
return
button자동업데이트:
msgbox,,업데이트,밑의 자동업데이트 버튼을 누르면 업데이트가 진행됩니다.
return
button?:
run, 사용법.txt
return
좌표1:
msgbox,,,[ 날짜좌표 ]예매창 띄운후 좌표정할곳 우클릭시 자동입력 됩니다.
loop
{
Gui,Submit, Nohide
MouseGetPos, X, Y
guicontrol,,좌표xy1,%X%
guicontrol,,1,%Y%
Gui,Submit, Nohide
if (GetKeyState("RButton", "P")=1)
{
goto,처음
}
}
msgbox,,,좌표입력이 완료되었습니다.
return
좌표2:
msgbox,,,[ 회차좌표 ]예매창 띄운후 좌표정할곳 우클릭시 자동입력 됩니다.
loop
{
Gui,Submit, Nohide
MouseGetPos, X, Y
guicontrol,,좌표xy2,%X%
guicontrol,,2,%Y%
Gui,Submit, Nohide
if (GetKeyState("RButton", "P")=1)
{
goto,처음
}
}
return
좌표3:
msgbox,,,[ 다음단계좌표 ]예매창 띄운후 좌표정할곳 우클릭시 자동입력 됩니다.
loop
{
Gui,Submit, Nohide
MouseGetPos, X, Y
guicontrol,,좌표xy3,%X%
guicontrol,,3,%Y%
Gui,Submit, Nohide
if (GetKeyState("RButton", "P")=1)
{
goto,처음
}
}
return
좌표4:
msgbox,,,[ 좌석범위↖ ]예매창 띄운후 좌표정할곳 우클릭시 자동입력 됩니다.
loop
{
Gui,Submit, Nohide
MouseGetPos, X, Y
guicontrol,,좌표xy4,%X%
guicontrol,,4,%Y%
Gui,Submit, Nohide
if (GetKeyState("RButton", "P")=1)
{
goto,처음
}
}
return
좌표5:
msgbox,,,[ 좌석범위↘ ]예매창 띄운후 좌표정할곳 우클릭시 자동입력 됩니다.
loop
{
Gui,Submit, Nohide
MouseGetPos, X, Y
guicontrol,,좌표xy5,%X%
guicontrol,,5,%Y%
Gui,Submit, Nohide
if (GetKeyState("RButton", "P")=1)
{
goto,처음
}
}
return
좌표6:
msgbox,,,[ 좌석선택완료 ]예매창 띄운후 좌표정할곳 우클릭시 자동입력 됩니다.
loop
{
Gui,Submit, Nohide
MouseGetPos, X, Y
guicontrol,,좌표xy6,%X%
guicontrol,,6,%Y%
Gui,Submit, Nohide
if (GetKeyState("RButton", "P")=1)
{
goto,처음
}
}
return
색깔7:
msgbox,,,[ 티켓좌석색깔 ]예매창 띄운후 색깔정할곳 우클릭시 자동입력 됩니다.
loop
{
Gui,Submit, Nohide
MouseGetPos, X, Y
PixelGetColor,Pixel1,%X%,%Y%
Guicontrol,,색깔xy7,%Pixel1%
Gui,Submit, Nohide
if (GetKeyState("RButton", "P")=1)
{
goto,처음
}
}
return
색깔8:
msgbox,,,[ 1구역 취켓좌석색깔 ]예매창 띄운후 색깔정할곳 우클릭시 자동입력 됩니다.
loop
{
Gui,Submit, Nohide
MouseGetPos, X, Y
PixelGetColor,Pixel1,%X%,%Y%
Guicontrol,,색깔xy8,%Pixel1%
Gui,Submit, Nohide
if (GetKeyState("RButton", "P")=1)
{
goto,처음
}
}
return
색깔9:
msgbox,,,[ 2구역 취켓좌석색깔 ]예매창 띄운후 색깔정할곳 우클릭시 자동입력 됩니다.
loop
{
Gui,Submit, Nohide
MouseGetPos, X, Y
PixelGetColor,Pixel1,%X%,%Y%
Guicontrol,,색깔xy9,%Pixel1%
Gui,Submit, Nohide
if (GetKeyState("RButton", "P")=1)
{
goto,처음
}
}
return
좌표10:
msgbox,,,[ 좌석선택완료 ]예매창 띄운후 좌표정할곳 우클릭시 자동입력 됩니다.
loop
{
Gui,Submit, Nohide
MouseGetPos, X, Y
guicontrol,,좌표xy10,%X%
guicontrol,,10,%Y%
Gui,Submit, Nohide
if (GetKeyState("RButton", "P")=1)
{
goto,처음
}
}
return
좌표11:
msgbox,,,[ 1구역좌석범위↖ ]예매창 띄운후 좌표정할곳 우클릭시 자동입력 됩니다.
loop
{
Gui,Submit, Nohide
MouseGetPos, X, Y
guicontrol,,좌표xy11,%X%
guicontrol,,11,%Y%
Gui,Submit, Nohide
if (GetKeyState("RButton", "P")=1)
{
goto,처음
}
}
return
좌표12:
msgbox,,,[ 1구역좌석범위↘ ]예매창 띄운후 좌표정할곳 우클릭시 자동입력 됩니다.
loop
{
Gui,Submit, Nohide
MouseGetPos, X, Y
guicontrol,,좌표xy12,%X%
guicontrol,,12,%Y%
Gui,Submit, Nohide
if (GetKeyState("RButton", "P")=1)
{
goto,처음
}
}
return
좌표13:
msgbox,,,[ 2구역좌석범위↖ ]예매창 띄운후 좌표정할곳 우클릭시 자동입력 됩니다.
loop
{
Gui,Submit, Nohide
MouseGetPos, X, Y
guicontrol,,좌표xy13,%X%
guicontrol,,13,%Y%
Gui,Submit, Nohide
if (GetKeyState("RButton", "P")=1)
{
goto,처음
}
}
return
좌표14:
msgbox,,,[ 2구역좌석범위↘ ]예매창 띄운후 좌표정할곳 우클릭시 자동입력 됩니다.
loop
{
Gui,Submit, Nohide
MouseGetPos, X, Y
guicontrol,,좌표xy14,%X%
guicontrol,,14,%Y%
Gui,Submit, Nohide
if (GetKeyState("RButton", "P")=1)
{
goto,처음
}
}
return
좌표111:
msgbox,,,취켓팅 원하는 구역 선택
loop
{
Gui,Submit, Nohide
Gui,2:Submit,nohide
MouseGetPos, X, Y
guicontrol,,좌표x1,%X%
guicontrol,,좌표y1,%Y%
Gui,Submit, Nohide
if (GetKeyState("RButton", "P")=1)
{
goto,처음
}
}
return
좌표222:
msgbox,,,취켓팅 원하는 구역 선택
loop
{
Gui,Submit, Nohide
Gui,2:Submit,nohide
MouseGetPos, X, Y
guicontrol,,좌표x2,%X%
guicontrol,,좌표y2,%Y%
Gui,Submit, Nohide
if (GetKeyState("RButton", "P")=1)
{
goto,처음
}
}
return
button저장하기:
gui,submit,nohide
Gui,2:Submit,nohide
filedelete save1.ini
IniWrite, %좌표xy1%, Save1.ini, 내용, 1
IniWrite, %1%, Save1.ini, 내용, 2
IniWrite, %좌표xy2%, Save1.ini, 내용, 3
IniWrite, %2%, Save1.ini, 내용, 4
IniWrite, %좌표xy3%, Save1.ini, 내용, 5
filedelete save2.ini
IniWrite, %3%, Save2.ini, 내용, 6
IniWrite, %좌표xy4%, Save2.ini, 내용, 7
IniWrite, %4%, Save2.ini, 내용, 8
IniWrite, %좌표xy5%, Save2.ini, 내용, 9
IniWrite, %5%, Save2.ini, 내용, 10
filedelete save3.ini
IniWrite, %좌표xy6%, Save3.ini, 내용, 11
IniWrite, %6%, Save3.ini, 내용, 12
IniWrite, %색깔xy7%, Save3.ini, 내용, 13
IniWrite, %색깔xy8%, Save3.ini, 내용, 14
IniWrite, %색깔xy9%, Save3.ini, 내용, 15
filedelete save4.ini
IniWrite, %좌표xy10%, Save4.ini, 내용, 16
IniWrite, %10%, Save4.ini, 내용, 17
IniWrite, %좌표xy11%, Save4.ini, 내용, 18
IniWrite, %11%, Save4.ini, 내용, 19
IniWrite, %좌표xy12%, Save4.ini, 내용, 20
filedelete save5.ini
IniWrite, %12%, Save5.ini, 내용, 21
IniWrite, %좌표xy13%, Save5.ini, 내용, 22
IniWrite, %13%, Save5.ini, 내용, 23
IniWrite, %좌표xy14%, Save5.ini, 내용, 24
IniWrite, %14%, Save5.ini, 내용, 25
filedelete save6.ini
IniWrite, %티켓순간%, Save6.ini, 내용, 26
IniWrite, %취켓순간%, Save6.ini, 내용, 27
IniWrite, %오차%, Save6.ini, 내용, 28
IniWrite, %구역딜%, Save6.ini, 내용, 29
msgbox,,저장하기, 저장이 완료 되었습니다.
Return
button불러오기:
gui,submit,nohide
Gui,2:Submit,nohide
IniRead,내용저장1, Save1.ini, 내용,1
IniRead,내용저장2, Save1.ini, 내용,2
IniRead,내용저장3, Save1.ini, 내용,3
IniRead,내용저장4, Save1.ini, 내용,4
IniRead,내용저장5, Save1.ini, 내용,5
IniRead,내용저장6, Save2.ini, 내용,6
IniRead,내용저장7, Save2.ini, 내용,7
IniRead,내용저장8, Save2.ini, 내용,8
IniRead,내용저장9, Save2.ini, 내용,9
IniRead,내용저장10, Save2.ini, 내용,10
IniRead,내용저장11, Save3.ini, 내용,11
IniRead,내용저장12, Save3.ini, 내용,12
IniRead,내용저장13, Save3.ini, 내용,13
IniRead,내용저장14, Save3.ini, 내용,14
IniRead,내용저장15, Save3.ini, 내용,15
IniRead,내용저장16, Save4.ini, 내용,16
IniRead,내용저장17, Save4.ini, 내용,17
IniRead,내용저장18, Save4.ini, 내용,18
IniRead,내용저장19, Save4.ini, 내용,19
IniRead,내용저장20, Save4.ini, 내용,20
IniRead,내용저장21, Save5.ini, 내용,21
IniRead,내용저장22, Save5.ini, 내용,22
IniRead,내용저장23, Save5.ini, 내용,23
IniRead,내용저장24, Save5.ini, 내용,24
IniRead,내용저장25, Save5.ini, 내용,25
IniRead,내용저장26, Save6.ini, 내용,26
IniRead,내용저장27, Save6.ini, 내용,27
IniRead,내용저장28, Save6.ini, 내용,28
IniRead,내용저장29, Save6.ini, 내용,29
guicontrol,,좌표xy1,%내용저장1%
guicontrol,,1,%내용저장2%
guicontrol,,좌표xy2,%내용저장3%
guicontrol,,2,%내용저장4%
guicontrol,,좌표xy3,%내용저장5%
guicontrol,,3,%내용저장6%
guicontrol,,좌표xy4,%내용저장7%
guicontrol,,4,%내용저장8%
guicontrol,,좌표xy5,%내용저장9%
guicontrol,,5,%내용저장10%
guicontrol,,좌표xy6,%내용저장11%
guicontrol,,6,%내용저장12%
guicontrol,,색깔xy7,%내용저장13%
guicontrol,,색깔xy8,%내용저장14%
guicontrol,,색깔xy9,%내용저장15%
guicontrol,,좌표xy10,%내용저장16%
guicontrol,,10,%내용저장17%
guicontrol,,좌표xy11,%내용저장18%
guicontrol,,11,%내용저장19%
guicontrol,,좌표xy12,%내용저장20%
guicontrol,,12,%내용저장21%
guicontrol,,좌표xy13,%내용저장22%
guicontrol,,13,%내용저장23%
guicontrol,,좌표xy14,%내용저장24%
guicontrol,,14,%내용저장25%
guicontrol,,티켓순간,%내용저장26%
guicontrol,,취켓순간,%내용저장27%
guicontrol,,오차,%내용저장28%
guicontrol,,구역딜,%내용저장29%
Msgbox,, 불러오기, 불러오기가 완료 되었습니다.
Return
자동:
msgbox,4,최신버전 다운로드,
(
최신버전 다운로드

현재사용 버전 1.0.0

매크로 파일은 폴더안에 자동 다운로드 됩니다.

업데이트가 되었는지는 다운후 파일 버전을 확인해주세요.

예(Y)를 누를시 다운로드 됩니다.

)
ifMsgbox, no, {
}else{
urldownloadtofile,http://white150.dothome.co.kr/all.zip,[돌핀준] 종합버전 1.0.0.zip
}
return
티켓주의:
msgbox,,,사용법 꼭 숙지후 사용바랍니다.
return
취켓주의:
msgbox,,,사용법 꼭 숙지후 사용바랍니다.
return           (          (            h            h            h   �4   V S _ V E R S I O N _ I N F O     ���                     