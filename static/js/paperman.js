
async function collectArxiv(topic_id, keywords, max_results, post_url, csrf_token) {
  if (keywords.trim() === "") {
    throw new Error("Keywords are required!");
  }

  const keywordArray = keywords.split(",").map(keyword => keyword.trim());
  var count = 0;

  for (let i = 0; i < keywordArray.length; i++) {
    const papers = await getArxivList(keywordArray[i], max_results);

    Array.from(papers).forEach(paper => {
      try {
        const title = paper.getElementsByTagName('title')[0].textContent;
        const authorNodeList = paper.getElementsByTagName('author');
        const author = Array.from(authorNodeList).map(a => a.getElementsByTagName('name')[0].textContent).join(', ');
        const publish_date = paper.getElementsByTagName('published')[0].textContent.split('T')[0];
        const url = paper.getElementsByTagName('id')[0].textContent;
        const abstract = paper.getElementsByTagName('summary')[0].textContent;
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
          citations: null,
          tags: '',
          abstract: abstract,
          note: '',
          topic_id: topic_id
        }, post_url, csrf_token);

        count += 1;
      } catch (error) {
        console.error(`Error while processing paper "${title}: ${error}`);
      }
    });
  }

  return count;
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
    console.log('Requesting to ' + url);
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

function renderTags(paper_id, tags) {
  const full_tags = ["📌", "🔎", "📖", "👍", "⭐", "✅"];
  const tooltip = {
    "📌": "Bookmark",
    "🔎": "Reading",
    "📖": "Read",
    "👍": "Like",
    "⭐": "Favorite",
    "✅": "Done",
  }
  const html = full_tags.map(tag => {
    if (tags.includes(tag)) {
      return `<button class="transparent active" onclick="onToggleTag(${paper_id}, '${tag}')" title="${tooltip[tag]}">${tag}</button>`;
    } else {
      return `<button class="transparent inactive" onclick="onToggleTag(${paper_id}, '${tag}')" title="${tooltip[tag]}">${tag}</button>`;
    }
  }).join('');

  document.getElementById(`tags-${paper_id}`).innerHTML = html;
}

function toggleTag(paper_id, tag, post_url, csrf_token) {
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
  }).then(response => response.json())
    .then(data => {
      renderTags(paper_id, data.tags);
    })
    .catch(error => {
      console.error('Error:', error);
    });
}

function onTagFilter(table_id, tag) {
  console.log(table_id);
  console.log(tag);

  const table = document.getElementById(table_id);
  const rows = table.getElementsByTagName('tr');

  if (tag == '🗙') {
    for (let i = 1; i < rows.length; i++) {
      rows[i].style.display = '';
    }
    return;
  }

  for (let i = 1; i < rows.length; i++) {
    const row = rows[i];
    const td = row.querySelector('td[id="tags"]');
    const tags = td.querySelectorAll('button.active');
    let concatenatedText = "";

    tags.forEach(tag => {
      concatenatedText += tag.innerText;
    });

    if (concatenatedText.includes(tag)) {
      row.style.display = '';
    } else {
      row.style.display = 'none';
    }
  }
}

async function renderPDF(frame, pdfUrl, scale) {
  const pdfBytes = await fetch(pdfUrl).then(res => res.arrayBuffer());
  const pdfjsDoc = await pdfjsLib.getDocument({ data: pdfBytes }).promise;
  const numPages = pdfjsDoc.numPages;
  const iframeDocument = frame.contentDocument || frame.contentWindow.document;

  iframeDocument.body.style.textAlign = 'center';
  iframeDocument.body.style.margin = '0';
  iframeDocument.body.style.position = 'relative';

  for (let i = 0; i < numPages; i++) {
    const pdfjsPage = await pdfjsDoc.getPage(i + 1);
    const viewport = pdfjsPage.getViewport({ scale: scale });
    const pageWrapper = document.createElement('div');
    pageWrapper.style.position = 'relative';
    pageWrapper.style.width = `${viewport.width}px`;
    pageWrapper.style.height = `${viewport.height}px`;
    pageWrapper.style.margin = '0 auto';

    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.height = viewport.height;
    canvas.width = viewport.width;
    canvas.style.display = 'block';
    canvas.style.border = '1px solid lightgray';
    canvas.style.pointerEvents = 'none';

    await pdfjsPage.render({
      canvasContext: context,
      viewport: viewport
    }).promise;

    const textLayer = document.createElement('div');
    textLayer.style.position = 'absolute';
    textLayer.style.top = '0';
    textLayer.style.left = '0';
    textLayer.style.width = `${viewport.width}px`;
    textLayer.style.height = `${viewport.height}px`;
    textLayer.style.pointerEvents = 'auto';
    textLayer.style.userSelect = 'text';
    textLayer.style.zIndex = '10';

    const textContent = await pdfjsPage.getTextContent();
    textContent.items.forEach(item => {
      const textDiv = document.createElement('span');
      textDiv.textContent = item.str;
      textDiv.style.position = 'absolute';
      const [fontSize, , , , x, y] = item.transform;
      const invertedY = viewport.height / scale - y - fontSize;
      textDiv.style.left = `${x * scale}px`;
      textDiv.style.top = `${invertedY * scale}px`;
      textDiv.style.fontSize = `${fontSize * scale}px`;
      textDiv.style.backgroundColor = 'white';
      textDiv.style.color = 'black';
      textDiv.style.padding = '1px';
      textDiv.style.display = 'inline-block';

      if (item.fontName) {
        textDiv.style.fontFamily = item.fontName;
      }

      textLayer.appendChild(textDiv);
    });

    pageWrapper.appendChild(canvas);
    pageWrapper.appendChild(textLayer);
    iframeDocument.body.appendChild(pageWrapper);
  }
}

async function extractPDF(pdfUrl) {
  const pdfBytes = await fetch(pdfUrl).then(res => res.arrayBuffer());
  const pdfjsDoc = await pdfjsLib.getDocument({ data: pdfBytes }).promise;
  let fullText = '';

  for (let pageNum = 1; pageNum <= pdfjsDoc.numPages; pageNum++) {
    const page = await pdfjsDoc.getPage(pageNum);
    const textContent = await page.getTextContent();
    const pageText = textContent.items.map(item => item.str).join(' ');
    fullText += pageText + '\n';
  }

  return fullText;
}

function reportError(e) {
  const msg = "Error: " + (e.message || e.toString());
  alert(msg);
  console.error(msg);
}

function updateStatus() {
  const status = document.getElementById("status")

  fetch("/home/status/")
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP Error(${response.status})`);
      }
      return response.json();
    })
    .then(data => {
      status.innerText = data.status;
    })
    .catch(error => {
      status.innerText = error;
    });
}