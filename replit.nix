{ pkgs }: {
  deps = [
    pkgs.python313
    pkgs.python313Packages.gunicorn
    pkgs.python313Packages.flask # Ou qualquer outra biblioteca que você esteja usando
    # Adicione outras dependências aqui
  ];
}
