# dotbins - Add platform-specific binaries to PATH
let _os = (sys).host.name | str downcase
let _os = if $_os == "darwin" { "macos" } else { $_os }

let _arch = (sys).host.arch
let _arch = if $_arch == "x86_64" { "amd64" } else if $_arch in ["aarch64", "arm64"] { "arm64" } else { $_arch }

$env.PATH = ($env.PATH | prepend $"$HOME/.dotbins/$_os/$_arch/bin")
