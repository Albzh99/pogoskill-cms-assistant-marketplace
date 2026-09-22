$script:CmsCredentialTarget = 'PoGoskillCMS/OpenAPI'

if (-not ('CmsCredentialNative' -as [type])) {
  Add-Type -TypeDefinition @'
using System;
using System.ComponentModel;
using System.Runtime.InteropServices;

public static class CmsCredentialNative
{
    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    private struct Credential
    {
        public uint Flags;
        public uint Type;
        public string TargetName;
        public string Comment;
        public System.Runtime.InteropServices.ComTypes.FILETIME LastWritten;
        public uint CredentialBlobSize;
        public IntPtr CredentialBlob;
        public uint Persist;
        public uint AttributeCount;
        public IntPtr Attributes;
        public string TargetAlias;
        public string UserName;
    }

    [DllImport("advapi32.dll", EntryPoint = "CredWriteW", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern bool CredWrite(ref Credential credential, uint flags);

    [DllImport("advapi32.dll", EntryPoint = "CredReadW", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern bool CredRead(string target, uint type, uint flags, out IntPtr credentialPtr);

    [DllImport("advapi32.dll", SetLastError = false)]
    private static extern void CredFree(IntPtr buffer);

    public static void Write(string target, string userName, string secret)
    {
        IntPtr blob = Marshal.StringToCoTaskMemUni(secret);
        try
        {
            Credential credential = new Credential();
            credential.Type = 1; // CRED_TYPE_GENERIC
            credential.TargetName = target;
            credential.CredentialBlobSize = (uint)(secret.Length * 2);
            credential.CredentialBlob = blob;
            credential.Persist = 2; // CRED_PERSIST_LOCAL_MACHINE
            credential.UserName = userName;
            if (!CredWrite(ref credential, 0))
                throw new Win32Exception(Marshal.GetLastWin32Error());
        }
        finally
        {
            Marshal.ZeroFreeCoTaskMemUnicode(blob);
        }
    }

    public static string Read(string target)
    {
        IntPtr credentialPtr;
        if (!CredRead(target, 1, 0, out credentialPtr))
        {
            int error = Marshal.GetLastWin32Error();
            if (error == 1168) return null; // ERROR_NOT_FOUND
            throw new Win32Exception(error);
        }

        try
        {
            Credential credential = (Credential)Marshal.PtrToStructure(credentialPtr, typeof(Credential));
            if (credential.CredentialBlob == IntPtr.Zero || credential.CredentialBlobSize == 0)
                return String.Empty;
            return Marshal.PtrToStringUni(credential.CredentialBlob, (int)credential.CredentialBlobSize / 2);
        }
        finally
        {
            CredFree(credentialPtr);
        }
    }
}
'@
}

function Set-CmsStoredApiKey {
  param([Parameter(Mandatory = $true)][string]$ApiKey)
  if ([string]::IsNullOrWhiteSpace($ApiKey) -or $ApiKey.Trim().Length -lt 20) {
    throw 'CMS API key appears incomplete; credential was not saved.'
  }
  if ($ApiKey.Trim() -notmatch '^AFS[0-9A-Za-z-]+$') {
    throw 'Clipboard does not contain a valid CMS API key; credential was not saved.'
  }
  [CmsCredentialNative]::Write($script:CmsCredentialTarget, 'X-API-KEY', $ApiKey.Trim())
}

function Get-CmsStoredApiKey {
  return [CmsCredentialNative]::Read($script:CmsCredentialTarget)
}

