using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;

// 在构建电脑预编译，客户电脑无需 PowerShell、csc.exe 或动态编译。
internal static class WebView2Probe
{
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, ExactSpelling = true, SetLastError = true)]
    private static extern IntPtr LoadLibraryExW(string path, IntPtr reserved, uint flags);
    [DllImport("kernel32.dll", CharSet = CharSet.Ansi, ExactSpelling = true, SetLastError = true)]
    private static extern IntPtr GetProcAddress(IntPtr module, string name);
    [DllImport("kernel32.dll", ExactSpelling = true)]
    private static extern bool FreeLibrary(IntPtr module);
    [UnmanagedFunctionPointer(CallingConvention.StdCall, CharSet = CharSet.Unicode)]
    private delegate int Query([MarshalAs(UnmanagedType.LPWStr)] string folder, out IntPtr version);

    private static bool Check(Query query, string folder, string expected, StringBuilder report)
    {
        IntPtr value = IntPtr.Zero;
        try
        {
            int result = query(folder, out value);
            string version = value == IntPtr.Zero ? "<none>" : Marshal.PtrToStringUni(value);
            report.AppendLine(String.Format("{0}: HRESULT=0x{1:X8} | version={2}",
                folder == null ? "Default" : "Directory", unchecked((uint)result), version));
            return result == 0 && version == expected;
        }
        finally
        {
            if (value != IntPtr.Zero) Marshal.FreeCoTaskMem(value);
        }
    }

    // 0=运行时可用；1=运行时检测不通过；2=检测工具故障，不能据此卸载运行时。
    private static int Main(string[] args)
    {
        if (args.Length != 4) return 2;
        StringBuilder report = new StringBuilder();
        IntPtr module = IntPtr.Zero;
        int exitCode = 2;
        try
        {
            report.AppendLine("Probe build: precompiled-net4-x64-v1");
            report.AppendLine("Time: " + DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"));
            report.AppendLine("CLR: " + Environment.Version);
            report.AppendLine("Process bits: " + (IntPtr.Size * 8));
            report.AppendLine("Loader: " + args[0]);
            report.AppendLine("Runtime folder: " + args[1]);
            report.AppendLine("Expected version: " + args[3]);
            if (IntPtr.Size != 8) throw new InvalidOperationException("检测工具必须以 x64 进程运行");
            module = LoadLibraryExW(Path.GetFullPath(args[0]), IntPtr.Zero, 8);
            if (module == IntPtr.Zero)
                throw new InvalidOperationException("加载检测 DLL 失败，Win32=" + Marshal.GetLastWin32Error());
            IntPtr address = GetProcAddress(module, "GetAvailableCoreWebView2BrowserVersionString");
            if (address == IntPtr.Zero)
                throw new InvalidOperationException("检测 DLL 缺少版本查询接口，Win32=" + Marshal.GetLastWin32Error());
            Query query = (Query)Marshal.GetDelegateForFunctionPointer(address, typeof(Query));
            bool directoryReady = Check(query, args[1], args[3], report);
            bool defaultReady = Check(query, null, args[3], report);
            exitCode = directoryReady && defaultReady ? 0 : 1;
        }
        catch (Exception exception)
        {
            report.AppendLine("Probe error: " + exception);
        }
        finally
        {
            if (module != IntPtr.Zero) FreeLibrary(module);
        }
        report.AppendLine("Exit code: " + exitCode);
        try { File.WriteAllText(args[2], report.ToString(), new UTF8Encoding(true)); }
        catch { return 2; }
        return exitCode;
    }
}
