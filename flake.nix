{
  description = "DIC - Declarative Imperative Configs";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
      pkgsFor = system: nixpkgs.legacyPackages.${system};
    in
    {
      packages = forAllSystems (system:
        let
          pkgs = pkgsFor system;
        in
        {
          default = pkgs.python3Packages.buildPythonApplication {
            pname = "dic";
            version = "0.0.1";
            pyproject = true;

            src = ./.;

            build-system = with pkgs.python3Packages; [ setuptools ];
            dependencies = with pkgs.python3Packages; [ jinja2 ];

            meta = {
              description = "Declerative Imperative Configs";
              mainProgram = "dic";
            };
          };
        });

      apps = forAllSystems (system: {
        default = {
          type = "app";
          program = "${self.packages.${system}.default}/bin/dic";
          meta.description = "Declerative Imperative Configs";
        };
      });

      devShells = forAllSystems (system:
        let
          pkgs = pkgsFor system;
        in
        {
          default = pkgs.mkShell {
            packages = [
              (pkgs.python3.withPackages (ps: [ ps.jinja2 ]))
            ];
          };
        });
    };
}
