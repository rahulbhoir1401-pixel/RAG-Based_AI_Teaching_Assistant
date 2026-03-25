Write-Host "Downloading portable FFmpeg..."
Invoke-WebRequest -Uri "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip" -OutFile "ffmpeg.zip"
Write-Host "Extracting..."
Expand-Archive -Path "ffmpeg.zip" -DestinationPath "ffmpeg_extracted" -Force
Write-Host "Moving ffmpeg.exe to project root..."
Move-Item -Path "ffmpeg_extracted\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe" -Destination ".\" -Force
Write-Host "Cleaning up..."
Remove-Item -Path "ffmpeg.zip"
Remove-Item -Path "ffmpeg_extracted" -Recurse -Force
Write-Host "Done! ffmpeg is now located in the project folder."
