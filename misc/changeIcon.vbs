Const DESKTOP = &H10&

Dim objShell
Dim objFolder
Dim objFolderItem
Dim objShortcut

Dim pairs(20)
pairs(0) = Array("Max Payne")
pairs(1) = Array("Dishonored")
pairs(2) = Array("The Witcher 2 Assassins of Kings Enhanced Edition")
pairs(3) = Array("Alan Wake")
pairs(4) = Array("Dark Souls Prepare to Die Edition")
pairs(5) = Array("Legend of Grimrock 2")
pairs(6) = Array("Tomb Raider")
pairs(7) = Array("Sniper Elite 3")
pairs(8) = Array("Brothers - A Tale of Two Sons")
pairs(9) = Array("Dead Space")
pairs(10) = Array("Antichamber")
pairs(11) = Array("Borderlands 2")
pairs(12) = Array("Worms Revolution")
pairs(13) = Array("LIMBO")
pairs(14) = Array("The Walking Dead")
pairs(15) = Array("Dragon Age Origins - Ultimate Edition")
pairs(16) = Array("VisualBoyAdvance - Shortcut")
pairs(17) = Array("Tom Clancy's Splinter Cell Blacklist")
pairs(18) = Array("Star Wars - Battlefront II")
pairs(19) = Array("Far Cry 3 Blood Dragon")
pairs(20) = Array("Amnesia The Dark Descent")

for each p in pairs
	Set objShell = CreateObject("Shell.Application")
	Set objFolder = objShell.NameSpace(DESKTOP)
    
	Set objFolderItem = objFolder.ParseName(p(0))
    Wscript.echo objFolder
    
	Set objShortcut = objFolderItem.GetLink
	
    'Set icoPath = "F:/Icons_A/" + p(0) + ".ico"
    
	'objShortcut.SetIconLocation icoPath, 0
	'objShortcut.Save
next