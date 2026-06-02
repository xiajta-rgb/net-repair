Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class WfpApi {
    [DllImport("fwpuclnt.dll", CharSet = CharSet.Unicode)]
    public static extern uint FwpmEngineOpen0(IntPtr serverName, uint authnService,
        IntPtr authIdentity, IntPtr session, out IntPtr engineHandle);
    [DllImport("fwpuclnt.dll")]
    public static extern uint FwpmEngineClose0(IntPtr engineHandle);
    [DllImport("fwpuclnt.dll")]
    public static extern uint FwpmFilterDeleteByKey0(IntPtr engineHandle, ref Guid filterKey);
    [DllImport("fwpuclnt.dll")]
    public static extern uint FwpmSubLayerDeleteByKey0(IntPtr engineHandle, ref Guid subLayerKey);
}
"@

Write-Host "============================================================" -ForegroundColor Green
Write-Host "  飞书WFP规则清除工具" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

$engineHandle = [IntPtr]::Zero
$ret = [WfpApi]::FwpmEngineOpen0([IntPtr]::Zero, 10, [IntPtr]::Zero, [IntPtr]::Zero, [ref]$engineHandle)

if ($ret -ne 0) {
    Write-Host "[ERROR] FwpmEngineOpen0 failed: 0x$($ret.ToString('X8'))" -ForegroundColor Red
    Read-Host "按回车退出"
    exit 1
}

Write-Host "[OK] WFP引擎已打开" -ForegroundColor Green

# 删除腾讯电脑管家TAONETFLOW相关过滤器
$taoFilters = @('e4a641e5-d35f-4726-8b3d-f026261818ab',
                 'ee90c253-3b67-49fe-bbed-f0c1d5660388',
                 '005c0421-7772-4d1b-acb7-6ed93ff89317')
$taoSublayer = '8c19c91f-4599-4931-b1cd-0da78dec1ede'

Write-Host ""
Write-Host "[1] 删除腾讯TAONETFLOW过滤器..." -ForegroundColor Yellow
$deleted = 0
foreach ($guid in $taoFilters) {
    $g = [Guid]$guid
    $ret = [WfpApi]::FwpmFilterDeleteByKey0($engineHandle, [ref]$g)
    if ($ret -eq 0) {
        Write-Host "  [OK] $guid" -ForegroundColor Green
        $deleted++
    } elseif ($ret -eq 0x80320003) {
        Write-Host "  [SKIP] $guid (不存在)" -ForegroundColor Gray
    } else {
        Write-Host "  [FAIL] $guid (0x$($ret.ToString('X8')))" -ForegroundColor Red
    }
}
Write-Host "  已删除 $deleted 个过滤器" -ForegroundColor Cyan

Write-Host ""
Write-Host "[2] 删除腾讯TAONETFLOW子层..." -ForegroundColor Yellow
$sl = [Guid]$taoSublayer
$ret = [WfpApi]::FwpmSubLayerDeleteByKey0($engineHandle, [ref]$sl)
if ($ret -eq 0) {
    Write-Host "  [OK] 子层已删除" -ForegroundColor Green
} elseif ($ret -eq 0x80320003) {
    Write-Host "  [SKIP] 子层不存在" -ForegroundColor Gray
} else {
    Write-Host "  [FAIL] (0x$($ret.ToString('X8')))" -ForegroundColor Red
}

[WfpApi]::FwpmEngineClose0($engineHandle) | Out-Null
Write-Host ""
Write-Host "[OK] WFP引擎已关闭" -ForegroundColor Green

Write-Host ""
Write-Host "[3] 重置网络协议栈..." -ForegroundColor Yellow
netsh winsock reset
ipconfig /flushdns
Write-Host "  完成" -ForegroundColor Green

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  修复完成！" -ForegroundColor Green
Write-Host ""
Write-Host "  重要：必须重启电脑才能使更改生效！" -ForegroundColor Cyan
Write-Host "  重启后飞书应该可以正常访问。" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Green
Read-Host "按回车退出"