{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      packages.wordlebot = pkgs.poetry2nix.mkPoetryApplication {
        projectDir = ./.;
        overrides = pkgs.poetry2nix.overrides.withDefaults (
          self: super: {
            irccodes = super.irccodes.overridePythonAttrs (
              {
                format = "setuptools";
              }
            );
            autocommand = super.autocommand.overridePythonAttrs (
              {
                format = "setuptools";
              }
            );
            annotated-types = super.annotated-types.overridePythonAttrs (
              {
                format = "other";
                # nativeBuildInputs = [super.hatchling super.flake8];
                dontBuild = true;
                buildPhase = null;
              }
            );
            pydantic-core = super.annotated-types.overridePythonAttrs (
              {
                nativeBuildInputs = [pkgs.maturin];
              }
            );
          }
        );
      };

      defaultPackage = self.packages.${system}.wordlebot;

      devShell = pkgs.mkShell {
        inputsFrom = builtins.attrValues self.packages.${system};
      };

      formatter = pkgs.alejandra;
    });
}
