export const informationPages: Record<
  string,
  { title: string; paragraphs: string[] }
> = {
  about: {
    title: "About Smeltery Skills",
    paragraphs: [
      "Smeltery Skills is a public library of portable workflows for coding agents. Each skill describes a focused job: planning a change, investigating a bug, writing tests, reviewing code, or handing work to another person. The goal is to make useful practices easy to discover and repeat.",
      "The canonical instructions live in the smeltery/skills GitHub repository. This website renders those files into a searchable reference and provides installation commands. You can inspect the source, propose improvements, and choose only the skills that fit your work. The website does not run an agent for you or require an account.",
      "Skills and repository content are distributed under the PolyForm Shield license. Read the repository license before reusing or redistributing the material. Smeltery maintains the project in public, with contribution guidance and issue tracking on GitHub.",
    ],
  },
  contact: {
    title: "Contact & feedback",
    paragraphs: [
      "The best place to contact the Smeltery Skills maintainers is the public issue tracker at https://github.com/smeltery/skills/issues. Use it to report a broken page, suggest a workflow, describe a skill that needs clearer instructions, or ask a question about the project. Search existing issues first so related conversations stay together.",
      "For a website problem, include the page URL, what you expected, what happened, and your browser or device where relevant. For a skill problem, include the skill name and a minimal example that explains the issue. Remove credentials, private code, personal information, and other sensitive details before posting: GitHub issues are public.",
      "Changes can be proposed through a pull request in the same repository. Please read docs/contributing.md first. This is a community-maintained project; no guaranteed response time or support service is offered. The project does not publish a business mailing address or telephone support line.",
    ],
  },
  privacy: {
    title: "Privacy",
    paragraphs: [
      "Smeltery Skills is a public documentation website hosted on Vercel. The site does not provide accounts, checkout, or a form that collects personal information. Skill search and filtering happen in your browser. Search terms are reflected in the page URL, so they may be visible in your browser history and to anyone with whom you share that link.",
      "The site does not add advertising trackers or analytics scripts. Fonts are served with the website. The hosting provider may process ordinary request information such as IP addresses, browser information, requested paths, and timestamps to deliver the service, prevent abuse, and diagnose errors. Vercel’s own privacy policy describes its handling of that information: https://vercel.com/legal/privacy-policy.",
      "Links to GitHub and other external services take you to services with their own privacy practices. Public issues and pull requests are handled by GitHub. Do not include secrets or personal information in public reports. For questions about this website’s behavior, use https://github.com/smeltery/skills/issues. This page describes the current site; it will be updated if data collection changes.",
    ],
  },
};
