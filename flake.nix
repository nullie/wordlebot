{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    poetry2nix,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {
        inherit system;
      };
    in {
      packages.wordlebot = pkgs.poetry2nix.mkPoetryApplication {
        projectDir = ./.;
        overrides = pkgs.poetry2nix.overrides.withDefaults (
          self: super: {
            irccodes = super.irccodes.overridePythonAttrs {
              format = "setuptools";
            };
            autocommand = super.autocommand.overridePythonAttrs {
              format = "setuptools";
            };
            annotated-types = super.annotated-types.overrideAttrs (
              old: {
                format = "setuptools";
                nativeBuildInputs =
                  (old.nativeBuildInputs or [])
                  ++ [
                    self.hatchling
                    self.flake8
                  ];
              }
            );
            pydantic = super.pydantic.overridePythonAttrs (
              old: {
                format = "pyproject";
                nativeBuildInputs =
                  (old.nativeBuildInputs or [])
                  ++ [
                    self.hatchling
                    self.hatch-fancy-pypi-readme
                  ];
              }
            );
            pydantic-core = super.pydantic-core.overridePythonAttrs (
              old: {
                format = "pyproject";
                cargoDeps = pkgs.rustPlatform.fetchCargoTarball {
                  src = old.src;
                  hash = "sha256-X2s/VwM5emCq2bcEqcezoC9wnoP6UU0CgeM0x2PlzgI=";
                };
                nativeBuildInputs =
                  (old.nativeBuildInputs or [])
                  ++ [
                    pkgs.maturin
                    pkgs.rustPlatform.cargoSetupHook
                    pkgs.rustPlatform.maturinBuildHook
                  ];
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
