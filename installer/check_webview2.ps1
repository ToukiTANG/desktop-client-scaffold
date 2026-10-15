param([string]$LoaderPath, [string]$RuntimeFolder, [string]$ResultPath, [string]$ExpectedVersion)
# 兼容 Win7 PowerShell 2.0；只调用官方版本查询接口，不创建浏览器。
$source=@"
using System;
using System.Runtime.InteropServices;
public static class WebViewProbe {
    [DllImport("kernel32.dll",CharSet=CharSet.Unicode,SetLastError=true)]
    static extern IntPtr LoadLibraryExW(string file,IntPtr handle,uint flags);
    [DllImport("kernel32.dll",CharSet=CharSet.Ansi,ExactSpelling=true,SetLastError=true)]
    static extern IntPtr GetProcAddress(IntPtr module,string name);
    [DllImport("kernel32.dll")] static extern bool FreeLibrary(IntPtr module);
    [UnmanagedFunctionPointer(CallingConvention.StdCall,CharSet=CharSet.Unicode)]
    delegate int Query([MarshalAs(UnmanagedType.LPWStr)] string folder,out IntPtr version);
    public static string Check(string dll,string folder) {
        IntPtr module=LoadLibraryExW(dll,IntPtr.Zero,8);
        if(module==IntPtr.Zero)return "LoadLibrary failed: Win32="+Marshal.GetLastWin32Error();
        IntPtr value=IntPtr.Zero;
        try {
            IntPtr address=GetProcAddress(module,"GetAvailableCoreWebView2BrowserVersionString");
            if(address==IntPtr.Zero)return "GetProcAddress failed: Win32="+Marshal.GetLastWin32Error();
            Query query=(Query)Marshal.GetDelegateForFunctionPointer(address,typeof(Query));
            int result=query(folder,out value);
            return "HRESULT=0x"+unchecked((uint)result).ToString("X8")+" | version="+(value==IntPtr.Zero?"<none>":Marshal.PtrToStringUni(value));
        } finally {
            if(value!=IntPtr.Zero)Marshal.FreeCoTaskMem(value);
            FreeLibrary(module);
        }
    }
}
"@
try {
    Add-Type -TypeDefinition $source -ErrorAction Stop
    if ([IntPtr]::Size -ne 8) { throw '必须通过 64 位 PowerShell 检测 x64 加载器' }
    $message = [WebViewProbe]::Check($LoaderPath, $RuntimeFolder)
    # 指定目录与默认发现都要可用，防止安装成功后软件仍找不到运行时。
    $defaultMessage = [WebViewProbe]::Check($LoaderPath, $null)
    [IO.File]::WriteAllText($ResultPath, $message + [Environment]::NewLine + 'Default: ' + $defaultMessage, [Text.Encoding]::UTF8)
    if (($defaultMessage -eq ('HRESULT=0x00000000 | version=' + $ExpectedVersion)) -and $message -eq ('HRESULT=0x00000000 | version=' + $ExpectedVersion)) { exit 0 }
    exit 1
} catch {
    [IO.File]::WriteAllText($ResultPath, $_.Exception.Message, [Text.Encoding]::UTF8)
    exit 2
}
