function t() {
  p = document.getElementsByName('quote-p');
  quote = p[0];
  quote.textContent = '{{ translation }}'//'In valiant heart nothing impossible.';

  button = document.getElementsByName('t-button');
  button = button[0];
  button.textContent = '{{ language }}' //"French";
  button.onclick = o;
}

function o() {
  p = document.getElementsByName('quote-p');
  quote = p[0];
  quote.textContent = '{{ quote }}' //'“À vaillant coeur rien d’impossible.”';

  button = document.getElementsByName('t-button');
  button = button[0];
  button.textContent = "Translate";
  button.onclick = t;
}
<select name="lang">
  {% for lang, name in langs.items() %}
    <option value={{ lang }}>{{ name }}</option>
  {% endfor %}
</select>
<select name="testament">
  {% for testament, name in testaments.items() %}
    <option value={{ testament }}>{{ name }}</option>
  {% endfor %}
</select>
