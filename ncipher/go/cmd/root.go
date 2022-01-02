package cmd

import "github.com/spf13/cobra"

var rootCmd = &cobra.Command{
	Use:   "ncipher",
	Short: "ncipher go test commands",
}

func Execute() {
	cobra.CheckErr(rootCmd.Execute())
}

func init() {
}
