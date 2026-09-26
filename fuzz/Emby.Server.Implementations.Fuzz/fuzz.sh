#!/bin/sh

set -e

dotnet build -c Release ../../Jellyfin.Server.Implementations/Jellyfin.Server.Implementations.csproj --output bin
sharpfuzz bin/Jellyfin.Server.Implementations.dll
cp bin/Jellyfin.Server.Implementations.dll .

dotnet build
mkdir -p Findings
AFL_SKIP_BIN_CHECK=1 afl-fuzz -i "Testcases/$1" -o "Findings/$1" -t 5000 ./bin/Debug/net10.0/Emby.Server.Implementations.Fuzz "$1"
