<script>
    import { geoPath, geoNaturalEarth1 } from  "d3";
    export let  dataset  =  [];
    const  projection  =  geoNaturalEarth1();
    const  path  =  geoPath(projection);
</script>

{#each  dataset  as data}
    <path  d={path(data)} />
{/each}