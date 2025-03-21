
async function collectArxiv(topic_id, keywords, max_results, post_url, csrf_token) {
  if (keywords.trim() === "") {
    alert("Keywords are required!");
    return;
  }

  try {
    const papers = await getArxivList(keywords, max_results);

    Array.from(papers).forEach(paper => {
      const title = paper.getElementsByTagName('title')[0].textContent;
      const authorNodeList = paper.getElementsByTagName('author');
      const author = Array.from(authorNodeList).map(a => a.getElementsByTagName('name')[0].textContent).join(', ');
      const publish_date = paper.getElementsByTagName('published')[0].textContent.split('T')[0];
      const url = paper.getElementsByTagName('id')[0].textContent;
      const note = paper.getElementsByTagName('summary')[0].textContent;
      const pdf_url = url.replace('/abs/', '/pdf/');

      addPaper({
        title: title,
        author: author,
        publisher: 'arXiv',
        publish_date: publish_date,
        doi: '',
        url: url,
        pdf_url: pdf_url,
        pdf_name: title.replace(/\s/g, '_') + '.pdf',
        citations: '0',
        tags: '',
        note: note,
        topic_id: topic_id
      }, post_url, csrf_token);
    });
  } catch (error) {
    console.error('Error fetching papers:', error);
  }

  window.location.reload();
}

function addPaper(paper, url, csrf_token) {
  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrf_token
    },
    body: JSON.stringify(paper)
  })
    .catch(error => console.error('Error adding paper:', error));
}

async function getArxivList(keywords, max_results) {
  const researchTopic = encodeURIComponent(keywords);
  const url = `https://export.arxiv.org/api/query?search_query=all:${researchTopic}&start=0&max_results=${max_results}&sortBy=relevance&sortOrder=descending`;

  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    const data = await response.text();
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(data, "text/xml");
    return xmlDoc.getElementsByTagName('entry');
  } catch (error) {
    console.error('Error fetching arXiv data:', error);
    return [];
  }
}

function renderTags(paper_id, tags, csrf_token) {
  const full_tags = ["📌", "🔎", "📖", "👍", "⭐", "💡", "✅"];
  const tooltip = {
    "📌": "Bookmark",
    "🔎": "Reading",
    "📖": "Read",
    "👍": "Like",
    "⭐": "Favorite",
    "💡": "Idea",
    "✅": "Done",
  }
  const html = full_tags.map(tag => {
    if (tags.includes(tag)) {
      return `<button class="transparent" onclick="onToggleTag(${paper_id}, '${tag}')" title="${tooltip[tag]}">${tag}</button>`;
    } else {
      return `<button class="transparent inactive" onclick="onToggleTag(${paper_id}, '${tag}')" title="${tooltip[tag]}">${tag}</button>`;
    }
  }).join('');

  document.getElementById(`tag-${paper_id}`).innerHTML = html;
}

function toggleTag(paper_id, tag, post_url, csrf_token) {
  console.log(`{paper_id}, {tag}`);

  fetch(post_url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrf_token
    },
    body: JSON.stringify({
      paper_id: paper_id,
      tag: tag
    })
  })
    .catch(error => {
      console.error('Error:', error);
    });

  window.location.reload();
}
