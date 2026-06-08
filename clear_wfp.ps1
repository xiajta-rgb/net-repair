Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class Wfp {
    [DllImport("fwpuclnt.dll", CharSet=CharSet.Unicode)]
    public static extern uint FwpmEngineOpen0(IntPtr a, uint b, IntPtr c, IntPtr d, out IntPtr e);
    [DllImport("fwpuclnt.dll")]
    public static extern uint FwpmEngineClose0(IntPtr a);
    [DllImport("fwpuclnt.dll")]
    public static extern uint FwpmSubLayerDeleteAll0(IntPtr a, IntPtr b);
}
"@

Write-Host "=== 清除WFP所有子层 ===" -ForegroundColor Green
$h = [IntPtr]::Zero
$r = [Wfp]::FwpmEngineOpen0([IntPtr]::Zero, 10, [IntPtr]::Zero, [IntPtr]::Zero, [ref]$h)
if ($h -ne [IntPtr]::Zero) {
    $r = [Wfp]::FwpmSubLayerDeleteAll0($h, [IntPtr]::Zero)
    Write-Host "已清除所有WFP子层 (返回值: $r)" -ForegroundColor Yellow
    [Wfp]::FwpmEngineClose0($h)
} else {
    Write-Host "WFP引擎打开失败" -ForegroundColor Red
}

Write-Host "`n=== 重置Winsock ===" -ForegroundColor Green
netsh winsock reset

Write-Host "`n=== 重启服务 ===" -ForegroundColor Green
net stop BFE /y 2>$null
net start BFE 2>$null

Write-Host "`n完成! 请重启电脑" -ForegroundColor Green
Start-Sleep 3