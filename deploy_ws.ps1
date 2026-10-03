# RTL-SDR WebSocket Deployment Script
# Usage: .\deploy_ws.ps1 <token> <action>

param(
    [Parameter(Mandatory=$true)]
    [string]$token,
    
    [Parameter(Mandatory=$false)]
    [string]$action = "deploy"
)

Add-Type -AssemblyName System.Net.WebSockets.Client
Add-Type -AssemblyName System.Threading

$ws = New-Object System.Net.WebSockets.ClientWebSocket
$ws.Options.SetRequestHeader("Authorization", "Bearer $token")

$uri = New-Object System.Uri("ws://homeassistant.local:8123/api/websocket")
$ct = New-Object System.Threading.CancellationToken($false)

Write-Host "=== Déploiement RTL-SDR via WebSocket API ==="
Write-Host "Action: $action"
Write-Host ""

function Send-Message {
    param([hashtable]$msg)
    $msg.id = $script:messageId++
    $json = $msg | ConvertTo-Json -Depth 10 -Compress
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
    $segment = New-Object System.ArraySegment[byte] -ArgumentList @(,$bytes)
    $ws.SendAsync($segment, [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $ct).Wait()
}

function Receive-Message {
    $buffer = New-Object byte[] 16384
    $segment = New-Object System.ArraySegment[byte] -ArgumentList @(,$buffer)
    $result = $ws.ReceiveAsync($segment, $ct).Result
    $json = [System.Text.Encoding]::UTF8.GetString($buffer, 0, $result.Count)
    return $json | ConvertFrom-Json
}

$messageId = 1

try {
    Write-Host "🔗 Connexion WebSocket..."
    $ws.ConnectAsync($uri, $ct).Wait()
    Write-Host "✅ Connecté: $($ws.State)"
    Write-Host ""
    
    # Auth
    $auth = @{
        type = "auth"
        access_token = $token
    }
    $json = $auth | ConvertTo-Json -Compress
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
    $segment = New-Object System.ArraySegment[byte] -ArgumentList @(,$bytes)
    $ws.SendAsync($segment, [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $ct).Wait()
    
    $response = Receive-Message
    Write-Host "Auth response: $($response.type)"
    
    if ($response.type -eq "auth_ok") {
        Write-Host "✅ Authentification réussie"
        Write-Host ""
        
        if ($action -eq "deploy") {
            # Deploy files
            Write-Host "📦 Déploiement des fichiers..."
            
            # Create directories first
            Write-Host "📁 Création des dossiers..."
            Send-Message @{
                type = "call_service"
                domain = "hassio"
                service = "addon_stdin"
                service_data = @{
                    addon = "a0d7b954_vscode"
                    input = @{
                        command = "mkdir -p /config/custom_components/rtl_dsr/translations && mkdir -p /config/www/rtl_dsr && echo OK"
                    }
                }
            }
            $response = Receive-Message
            Write-Host "  Réponse: $($response | ConvertTo-Json -Depth 5 -Compress)"
            Write-Host ""
            
            # Deploy manifest.json
            $files = @(
                @{local="custom_components/rtl_dsr/manifest.json"; remote="/config/custom_components/rtl_dsr/manifest.json"},
                @{local="custom_components/rtl_dsr/const.py"; remote="/config/custom_components/rtl_dsr/const.py"},
                @{local="custom_components/rtl_dsr/config_flow.py"; remote="/config/custom_components/rtl_dsr/config_flow.py"},
                @{local="custom_components/rtl_dsr/coordinator.py"; remote="/config/custom_components/rtl_dsr/coordinator.py"},
                @{local="custom_components/rtl_dsr/model.py"; remote="/config/custom_components/rtl_dsr/model.py"},
                @{local="custom_components/rtl_dsr/entity.py"; remote="/config/custom_components/rtl_dsr/entity.py"},
                @{local="custom_components/rtl_dsr/__init__.py"; remote="/config/custom_components/rtl_dsr/__init__.py"},
                @{local="custom_components/rtl_dsr/sensor.py"; remote="/config/custom_components/rtl_dsr/sensor.py"},
                @{local="custom_components/rtl_dsr/binary_sensor.py"; remote="/config/custom_components/rtl_dsr/binary_sensor.py"},
                @{local="custom_components/rtl_dsr/number.py"; remote="/config/custom_components/rtl_dsr/number.py"},
                @{local="custom_components/rtl_dsr/select.py"; remote="/config/custom_components/rtl_dsr/select.py"},
                @{local="custom_components/rtl_dsr/switch.py"; remote="/config/custom_components/rtl_dsr/switch.py"},
                @{local="custom_components/rtl_dsr/button.py"; remote="/config/custom_components/rtl_dsr/button.py"},
                @{local="custom_components/rtl_dsr/text.py"; remote="/config/custom_components/rtl_dsr/text.py"},
                @{local="custom_components/rtl_dsr/services.py"; remote="/config/custom_components/rtl_dsr/services.py"},
                @{local="custom_components/rtl_dsr/services.yaml"; remote="/config/custom_components/rtl_dsr/services.yaml"},
                @{local="custom_components/rtl_dsr/strings.json"; remote="/config/custom_components/rtl_dsr/strings.json"},
                @{local="custom_components/rtl_dsr/websocket_api.py"; remote="/config/custom_components/rtl_dsr/websocket_api.py"},
                @{local="custom_components/rtl_dsr/translations/fr.json"; remote="/config/custom_components/rtl_dsr/translations/fr.json"},
                @{local="panel/sdrplusplus/card.js"; remote="/config/www/rtl_dsr/card.js"},
                @{local="panel/sdrplusplus/sdr-plus-plus-card.js"; remote="/config/www/rtl_dsr/sdr-plus-plus-card.js"}
            )
            
            for ($i = 0; $i -lt $files.Count; $i++) {
                $file = $files[$i]
                $content = Get-Content $file.local -Raw -Encoding UTF8
                $bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
                $base64 = [System.Convert]::ToBase64String($bytes)
                $filename = Split-Path $file.local -Leaf
                $progress = "[$($i+1)/$($files.Count)]"
                
                Write-Host "$progress 📄 $filename"
                
                Send-Message @{
                    type = "call_service"
                    domain = "hassio"
                    service = "addon_stdin"
                    service_data = @{
                        addon = "a0d7b954_vscode"
                        input = @{
                            command = "echo '$base64' | base64 -d > $($file.remote) && echo OK"
                        }
                    }
                }
                $response = Receive-Message
            }
            
            Write-Host ""
            Write-Host "✅✅✅ Déploiement terminé ! ✅✅✅"
            Write-Host ""
            Write-Host "📋 Prochaines étapes :"
            Write-Host "   1. Redémarrez Home Assistant"
            Write-Host "   2. Ajoutez l'intégration RTL-SDR"
            Write-Host "   3. Ajoutez la ressource Lovelace: /local/rtl_dsr/card.js"
            Write-Host "   4. Ajoutez une carte: type: custom:sdr-plus-plus-card"
            
        } elseif ($action -eq "restart") {
            Write-Host "🔄 Redémarrage de Home Assistant..."
            Send-Message @{
                type = "call_service"
                domain = "homeassistant"
                service = "restart"
            }
            $response = Receive-Message
            Write-Host "✅ Redémarrage lancé"
            
        } elseif ($action -eq "verify") {
            Write-Host "🔍 Vérification des fichiers..."
            Send-Message @{
                type = "call_service"
                domain = "hassio"
                service = "addon_stdin"
                service_data = @{
                    addon = "a0d7b954_vscode"
                    input = @{
                        command = "ls -la /config/custom_components/rtl_dsr/"
                    }
                }
            }
            $response = Receive-Message
            Write-Host "Fichiers déployés:"
            Write-Host ($response | ConvertTo-Json -Depth 5)
        }
    } else {
        Write-Host "❌ Échec authentification: $($response | ConvertTo-Json)"
    }
    
} catch {
    Write-Host "❌ Erreur: $($_.Exception.Message)"
    Write-Host $_.Exception.StackTrace
} finally {
    $ws.CloseAsync([System.Net.WebSockets.WebSocketCloseStatus]::NormalClosure, "done", $ct).Wait()
    Write-Host ""
    Write-Host "🔌 WebSocket fermé"
}
