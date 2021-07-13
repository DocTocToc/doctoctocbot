<script>
  import {
    Page,
    Navbar,
    NavTitle,
    NavTitleLarge,
    Link,
    Toolbar,
    Block,
    List,
    ListItem
  } from 'framework7-svelte';

  import Disciplines from "../components/Disciplines.svelte";
  
</script>



<Page name="home">
  <!-- Top Navbar -->
  <Navbar large>
    <NavTitle>choice</NavTitle>
    <NavTitleLarge>choice</NavTitleLarge>
  </Navbar>
  <!-- Toolbar -->
  <Toolbar bottom>
    <Link>Left Link</Link>
    <Link>Right Link</Link>
  </Toolbar>
  <!-- Page content -->
  <Block strong>
    <p>Here is your blank Framework7 app. Let's see what we have here.</p>
  </Block>

   <Disciplines />
    
</Page>

