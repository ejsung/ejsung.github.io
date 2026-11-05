# Make the existing Jekyll Scholar BibTeX data searchable by the site's Lunr index.
# Runs at build time; no extra browser dependency or second publication list.
require "bibtex"
require "uri"

module EJSung
  class CommandPalettePublications < Jekyll::Generator
    safe true
    priority :high

    def generate(site)
      config = site.config.fetch("scholar", {})
      source = config.fetch("source", "./_bibliography")
      filename = config.fetch("bibliography", "references.bib")
      path = File.expand_path(File.join(source, filename), site.source)
      unless File.file?(path)
        Jekyll.logger.warn("Command palette:", "Bibliography not found: #{path}")
        site.data["command_palette_publications"] = []
        return
      end

      site.data["command_palette_publications"] = BibTeX.open(path, filter: :latex).entries.values.map do |entry|
        title = clean(entry[:title])
        author = clean(entry[:author])
        year = clean(entry[:year])
        venue = clean(entry[:journal] || entry[:booktitle] || entry[:publisher])
        abstract = clean(entry[:abstract])
        doi = clean(entry[:doi])
        eprint = clean(entry[:eprint])
        link = clean(entry[:url])

        url = if doi.match?(/\A10\.\d{4,9}\/.+\z/)
                "https://doi.org/#{URI::DEFAULT_PARSER.escape(doi)}"
              elsif link.match?(/\Ahttps?:\/\//i)
                link
              elsif eprint.match?(/\A\d{4}\.\d{4,5}(?:v\d+)?\z/)
                "https://arxiv.org/abs/#{eprint}"
              else
                (site.baseurl || "") + "/research/"
              end

        {
          "title" => title,
          "excerpt" => [author, year, venue, abstract].reject(&:empty?).join(" · ")[0, 550],
          "categories" => ["publication"],
          "tags" => ["publication", "paper", entry.type.to_s, year, venue].reject(&:empty?),
          "url" => url,
          "year" => year,
          "palette_type" => "publication"
        }
      end.reject { |publication| publication["title"].empty? }
    end

    private

    def clean(value)
      value.to_s.gsub(/[{}]/, "").gsub(/\s+/, " ").strip
    end
  end
end
