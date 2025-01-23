{ pkgs }: {
  deps = [
    pkgs.python310
    pkgs.python310Packages.gunicorn
    pkgs.python310Packages.flask # Ou qualquer outra biblioteca que você esteja usando
    pkgs.python310Packages.requests
    # Adicione outras dependências aqui
  ];
}
