# Build public, copyable BibTeX entries from the existing bibliography.
# Only citation fields are allowed; never publish Zotero attachment paths,
# annotations, or other local-library metadata in the page source.
require "bibtex"

module EJSung
  class PublicBibliographyBibtex < Jekyll::Generator
    safe true
    priority :high

    PUBLIC_FIELDS = %w[
      title author editor journal booktitle year month volume number pages
      publisher institution school organization address edition series
      doi eprint archiveprefix primaryclass url isbn issn
    ].freeze

    def generate(site)
      options = site.config.fetch("scholar", {})
      directory = options.fetch("source", "./_bibliography")
      filename = options.fetch("bibliography", "references.bib")
      path = File.expand_path(File.join(directory, filename), site.source)
      site.data["public_bibtex"] = {}
      return unless File.file?(path)

      bibliography = BibTeX.open(path)
      bibliography.entries.values.each do |entry|
        fields = PUBLIC_FIELDS.filter_map do |field|
          value = entry[field.to_sym]
          next if value.nil? || value.to_s.strip.empty?
          # Do not copy local file:// references or other non-web URLs.
          next if field == "url" && !value.to_s.match?(/\Ahttps?:\/\//i)

          # BibTeX-Ruby preserves TeX markup in unfiltered field values.
          "  #{field} = {#{value}}"
        end
        next if fields.empty?

        site.data["public_bibtex"][entry.key.to_s] =
          "@#{entry.type}{#{entry.key},\n#{fields.join(",\n")}\n}"
      end
    end
  end
end
