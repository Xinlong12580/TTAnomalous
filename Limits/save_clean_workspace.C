void save_clean_workspace(
      const char *input,
      const char *output = "workspace_clean.root")
  {
      TFile input_file(input, "READ");
      auto *workspace =
          dynamic_cast<RooWorkspace *>(input_file.Get("w"));

      if (!workspace) {
      }

      TFile output_file(output, "RECREATE");
      workspace->Write("w");
      output_file.Close();
  }
